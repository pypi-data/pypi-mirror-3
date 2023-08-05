# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-vcreview specific hooks and operations"""

__docformat__ = "restructuredtext en"

import re

from cubicweb import RegistryException
from cubicweb.server import hook
from cubicweb.selectors import is_instance, on_fire_transition
from cubicweb.hooks import notification

from cubes.vcsfile import hooks as vcsfile

IGNORE_FILES = set( ('README', 'series', 'status', '.hgignore', '.hgtags') )

def fire(patch, trname, comment):
    patch.cw_adapt_to('IWorkflowable').fire_transition(trname, comment)


class ForcePatchMIMETypeHook(hook.Hook):
    __regid__ = 'vcreview.add_version_content_hook'
    __select__ = hook.Hook.__select__ & is_instance('VersionContent')
    events = ('before_add_entity',)
    # ensure we're fired before AddVersionContentHook
    order = vcsfile.AddVersionContentHook.order - 1

    def __call__(self):
        vf = self.entity._vc_vf()
        if vf.repository.patchrepo_of:
            if vf.name in IGNORE_FILES:
                self.entity.cw_edited['data_format'] = u'text/plain'
            else:
                self.entity.cw_edited['data_format'] = u'text/x-diff'
            self.entity.cw_edited['data_encoding'] = vf.repository.encoding


class LinkOrCreatePatchOp(hook.DataOperationMixIn, hook.Operation):
    """operation to track patch's state according to incoming revisions"""
    containercls = list # operation order matters

    def precommit_event(self):
        for entity in self.get_data():
            patch = None
            # if the revision is a renaming another one which is linked to the
            # patch (take care DeletedVersionContent has no vc_rename relation)
            if getattr(entity, 'vc_rename', None) and entity.vc_rename[0].patch:
                patch = entity.vc_rename[0].patch
            else:
                # search for previous revision of the patch file
                for parent in entity.previous_versions():
                    if (entity.__regid__ == 'DeletedVersionContent' and
                        getattr(parent, 'reverse_vc_rename', None)):
                        return # skip file deleted because of renaming
                    if parent.patch:
                        patch = parent.patch
                        break
            # create a new patch entity if no one found or if found a closed
            # patch and this is not a file deletion
            if patch is None or (not patch.is_active() and entity.__regid__ == 'VersionContent'):
                revision = entity.rev
                patch = self.session.create_entity(
                    'Patch', originator=revision.author, branch=revision.branch,
                    patch_repository=revision.from_repository, patch_name=entity.file.path)
            patch.set_relations(patch_revision=entity)
            # patch file is being removed: mark it on the patch entity if still
            # active
            if (entity.__regid__ == 'DeletedVersionContent'
                and entity.rev.branch == patch.branch
                and patch.is_active()):
                MarkPatchAsDeletedOp.get_instance(self.session).add_data(patch)


class LinkOrCreatePatchHook(hook.Hook):
    __regid__ = 'vcreview.create-patch'
    __select__ = hook.Hook.__select__ & is_instance('VersionContent',
                                                    'DeletedVersionContent')
    events = ('after_add_entity',)

    def __call__(self):
        entity = self.entity
        # skip file not from a patch repository
        if not entity.repository.patchrepo_of:
            return
        if entity.file.name in IGNORE_FILES:
            return
        LinkOrCreatePatchOp.get_instance(self._cw).add_data(entity)


class InitPatchCreatorHook(hook.Hook):
    __regid__ = 'vcreview.patch.created'
    __select__ = hook.Hook.__select__ & is_instance('Patch')
    events = ('before_add_entity',)
    category = 'metadata'

    def __call__(self):
        email = self.entity.originator.rsplit('<')[-1].rsplit('>')[0]
        rset = self._cw.execute('Any X WHERE X is CWUser, X use_email E, '
                                'E address %(email)s', {'email': email})
        relations = []
        for ueid, in rset:
            relations.append( (self.entity.eid, ueid) )
            # ensure user is in the nosy-list
            self._cw.execute('SET P nosy_list U WHERE P eid %(p)s, U eid %(u)s,'
                             'NOT P nosy_list U',
                             {'p': self.entity.eid, 'u': ueid})
        if relations:
            self._cw.add_relations([('created_by', relations),
                                    ('owned_by', relations)])


# use late operation to be executed after workflow operation
class SearchPatchStateInstructionOp(hook.DataOperationMixIn,
                                    hook.LateOperation):
    """search magic word in revision's commit message:

        <patch path> ready for review
        reject <patch path>
        fold <patch path>

    When found, the patch will be marked as pending review. You can put multiple
    instructions like this, one per line.
    """
    containercls = list
    def precommit_event(self):
        for rev in self.get_data():
            # search patches among files modified by the revision
            readycandidates = {}
            pendingcandidates = {}
            rejectcandidates = {}
            done = set()
            # consider both at_revision and from_revision since we want to be
            # able to use magic instructions for files not touched by the
            # revision (hence the at_revision), while DeletedVersionContent are
            # not referenced by at_revision, only from_revision.
            for vc in rev.reverse_at_revision + rev.reverse_from_revision:
                if vc.eid in done or not vc.patch:
                    continue
                done.add(vc.eid)
                pstate = vc.patch.cw_adapt_to('IWorkflowable').state
                if vc.__regid__ == 'VersionContent':
                    if pstate == 'in-progress':
                        readycandidates[vc.file.path.lower()] = vc.patch
                    elif pstate in ('pending-review', 'reviewed'):
                        pendingcandidates[vc.file.path.lower()] = vc.patch
                elif (pstate in vc.patch.non_final_states and
                      vc.__regid__ == 'DeletedVersionContent'):
                    rejectcandidates[vc.file.path.lower()] = vc.patch
            interestingwords = set( ('ready', 'applied', 'reject', 'fold') )
            interestingwords.update(readycandidates)
            interestingwords.update(pendingcandidates)
            interestingwords.update(rejectcandidates)
            # search for instruction
            for line in rev.description.splitlines():
                words = [w.lower() for w in re.findall('[-\.\w]+', line.strip())
                         if w.lower() in interestingwords]
                if len(words) < 2:
                    continue
                if words[1] in ('ready', 'pending') and words[0] in readycandidates:
                    fire(readycandidates.pop(words[0]),
                         'ask review', u'review asked by %s in %s' % (
                             rev.author, rev.dc_title()))
                elif words[0] in ('refuse', 'refused') and words[1] in pendingcandidates:
                    patch = pendingcandidates.pop(words[1])
                    fire(patch, 'ask rework', u'refused by %s in %s' % (
                        rev.author, rev.dc_title()))
                elif words[0] in ('reject', 'rejected') and words[1] in rejectcandidates:
                    patch = rejectcandidates.pop(words[1])
                    fire(patch, 'reject', u'rejected by %s in %s' % (
                        rev.author, rev.dc_title()))
                    self.ensure_wont_be_deleted(patch)
                elif words[0] in ('fold', 'folded') and words[1] in rejectcandidates:
                    patch = rejectcandidates.pop(words[1])
                    fire(patch, 'fold', u'folded by %s in %s' % (
                        rev.author, rev.dc_title()))
                    self.ensure_wont_be_deleted(patch)
                elif words[0] in ('apply', 'applied') and words[1] in rejectcandidates:
                    patch = rejectcandidates.pop(words[1])
                    fire(patch, 'apply', u'applied by %s' % rev.author)
                    self.ensure_wont_be_deleted(patch)
                    # XXX search source repository changeset id
                    #patch.set_relations(applied_at=rev)

    def ensure_wont_be_deleted(self, patch):
        op = MarkPatchAsDeletedOp.get_instance(self.session)
        try:
            # XXX op.remove_data(patch) once cw 3.10.9 is out
            op._container.remove(patch)
        except KeyError:
            pass


class RevisionAdded(hook.Hook):
    __regid__ = 'vcreview.auto-change-patch-state'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_add_entity',)

    def __call__(self):
        repo = self.entity.repository
        if repo.patchrepo_of:
            # patch repository
            SearchPatchStateInstructionOp.get_instance(self._cw).add_data(self.entity)


# use single last operation to be executed after all vcreview related operations
class MarkPatchAsDeletedOp(hook.DataOperationMixIn, hook.SingleLastOperation):
    def precommit_event(self):
        for patch in self.get_data():
            if self.session.added_in_transaction(patch.eid):
                self.session.execute('SET X in_state S WHERE X eid %(x)s, S name %(state)s',
                                     {'x': patch.eid, 'state': 'deleted'})
                # patch.cw_adapt_to('IWorkflowable').change_state('deleted')
            else:
                patch.cw_adapt_to('IWorkflowable').fire_transition('file deleted')


class SetReviewerOp(hook.DataOperationMixIn, hook.Operation):

    def precommit_event(self):
        for trinfo in self.get_data():
            patch = trinfo.for_entity
            patch.cw_adapt_to('IPatchReviewControl').set_reviewers(trinfo.transition)

class SetReviewerHook(hook.Hook):
    """register an operation to set a reviewer when the 'ask review' transition
    is fired
    """
    __regid__ = 'vcreview.set-reviewer'
    __select__ = hook.Hook.__select__ & on_fire_transition('Patch', 'ask review')
    events = ('after_add_entity',)

    def __call__(self):
        SetReviewerOp.get_instance(self._cw).add_data(self.entity)


class ReviewerSetHook(hook.Hook):
    """send a notification when a user is assigned to review a patch and ensure
    he is in the patch nosy-list
    """
    __regid__ = 'vcreview.reviewer-set'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_reviewer')
    events = ('after_add_relation',)

    def __call__(self):
        # send notification
        rset = self._cw.eid_rset(self.eidfrom)
        try:
            view = self._cw.vreg['views'].select(
                'vcreview.notifications.reviewer-set', self._cw,
                rset=rset, user=self._cw.eid_rset(self.eidto).get_entity(0, 0))
        except RegistryException:
            # view unregistered or unselectable
            return
        notification.RenderAndSendNotificationView(self._cw, view=view)
        # ensure user is in the nosy-list
        self._cw.execute('SET P nosy_list U WHERE P eid %(p)s, U eid %(u)s, NOT P nosy_list U',
                         {'p': self.eidfrom, 'u': self.eidto})

class UpdatePatchNameHook(hook.Hook):
    __regid__ = 'vcreview.patch-name-update'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_revision')
    events = ('after_add_relation',)

    def __call__(self):
        patch = self._cw.entity_from_eid(self.eidfrom)
        versioncontent = self._cw.entity_from_eid(self.eidto)
        if patch.patch_name != versioncontent.file.path:
            patch.set_attributes(patch_name=versioncontent.file.path)

from cubes.nosylist import hooks as nosylist
nosylist.S_RELS |= set(('has_activity', 'patch_revision'))
# XXX should add 'comments' relation in set below
nosylist.O_RELS |= set(('patch_repository', 'point_of'))
