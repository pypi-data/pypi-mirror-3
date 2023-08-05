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
"""cubicweb-vcreview postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

pwf = add_workflow(_('patch workflow'), 'Patch')

inprogress = pwf.add_state(_('in-progress'), initial=True)
pending    = pwf.add_state(_('pending-review'))
reviewed   = pwf.add_state(_('reviewed'))
applied    = pwf.add_state(_('applied'))
rejected   = pwf.add_state(_('rejected'))
folded     = pwf.add_state(_('folded'))
deleted    = pwf.add_state(_('deleted'))

pwf.add_transition(_('ask review'), inprogress, pending,
                   ('managers', 'users',)) # XXX patch owner only?
pwf.add_transition(_('accept'), (inprogress, pending), reviewed,
                   ('managers', 'committers', 'reviewers',),
                   ('X patch_repository R, R repository_committer U',
                    'X patch_repository R, R repository_reviewer U')) # XXX patch_reviewer/repo manager only?
pwf.add_transition(_('ask rework'), (pending, reviewed), inprogress,
                   ('managers', 'committers', 'reviewers',),
                   ('X patch_repository R, R repository_committer U',
                    'X patch_repository R, R repository_reviewer U')) # XXX patch_reviewer/repo manager only? ignore patch_reviewer if in reviewed state?
pwf.add_transition(_('fold'), (inprogress, pending, deleted, reviewed), folded,
                   ('managers', 'committers', 'reviewers',),
                   ('X patch_repository R, R repository_committer U',
                    'X patch_repository R, R repository_reviewer U')) # XXX patch owner/repo mananger only?
pwf.add_transition(_('apply'), (inprogress, pending, deleted, reviewed), applied,
                   ('managers', 'committers',),
                   'X patch_repository R, R repository_committer U')
pwf.add_transition(_('reject'), (inprogress, pending, deleted, reviewed), rejected,
                   ('managers', 'committers',),
                   'X patch_repository R, R repository_committer U')
# internal transition, not available through the ui
# XXX we've to put 'managers' group since transition without groups
# nor condition are fireable by anyone...
pwf.add_transition(_('file deleted'), (inprogress, pending, reviewed), deleted,
                   ('managers',))
# in case hooks following patch state made a mistake, we should be able to
# reopen the patch
pwf.add_transition(_('reopen'), deleted, inprogress,
                   ('managers', 'committers',),
                   'X patch_repository R, R repository_committer U')

commit()

# change task workflow permission
conditions = [
    # global reviewer / committer
    'Z has_activity X, U in_group G, G name IN ("reviewers", "committers")',
    # repository reviewer / committer
    'P has_activity X, P patch_repository R, EXISTS(R repository_reviewer U) OR EXISTS(R repository_committer U)',
    'IP has_activity X, IP point_of VC, P patch_revision VC, P patch_repository R, EXISTS(R repository_reviewer U) OR EXISTS(R repository_committer U)',
    # patch owner
    'P has_activity X, P owned_by U',
    'IP has_activity X, IP point_of VC, P patch_revision VC, P owned_by U',
    ]
task_wf = get_workflow_for('Task')
task_wf.transition_by_name('start').set_permissions(conditions=conditions, reset=False)
task_wf.transition_by_name('done').set_permissions(conditions=conditions, reset=False)
