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
"""cubicweb-trackervcs specific hooks and operations"""

import re

from rql import TypeResolverException

from cubicweb import typed_eid
from cubicweb.server import hook
from cubicweb.selectors import is_instance

from cubes.tracker import hooks as tracker

TICKET_EID_RGX = re.compile('#(\d+)')

def closed_eids(line):
    words = [w.lower() for w in re.findall('#?\w+', line.strip())]
    try:
        idx = words.index('closes')
    except ValueError:
        return ()
    return TICKET_EID_RGX.findall(' '.join(words[idx+1:]))


# search for ticket closing instructions #######################################

class SearchRevisionTicketOp(hook.DataOperationMixIn,
                             hook.Operation):
    """search magic words in revision's commit message:

        closes #<ticket eid>

    When found, the ticket is marked as closed by the revision and its state is
    changed.
    """
    def precommit_event(self):
        for rev in self.get_data():
            # search for instruction
            for line in rev.description.splitlines():
                for eid in closed_eids(line):
                    try:
                        rset = self.session.execute(
                            'Any X WHERE X eid %(x)s, X concerns P, '
                            'P source_repository R, R eid %(r)s',
                            {'x': typed_eid(eid), 'r': rev.repository.eid})
                    except TypeResolverException:
                        continue
                    if rset:
                        ticket = rset.get_entity(0, 0)
                        ticket.set_relations(closed_by=rev)
                        iwf = ticket.cw_adapt_to('IWorkflowable')
                        for tr in iwf.possible_transitions():
                            if tr.name in ('done', 'close'):
                                iwf.fire_transition(tr)
                                break

class RevisionAdded(hook.Hook):
    __regid__ = 'trackervcs.revision-to-ticket-state'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_add_entity',)
    category = 'autoset'

    def __call__(self):
        repo = self.entity.repository
        if repo.reverse_source_repository:
            SearchRevisionTicketOp.get_instance(self._cw).add_data(self.entity)


# synchronize  "P source_repository R" with ####################################
# "P has_apycot_environment PE AND PE local_repository R"

class SetSourceRepositoryOp(hook.Operation):
    def precommit_event(self):
        if not self.project.source_repository and self.projectenv.repository:
            self.project.set_relations(source_repository=self.projectenv.repository)

class ApycotEnvironmentAdded(hook.Hook):
    __regid__ = 'trackervcs.add-source-repository'
    __select__ = hook.Hook.__select__ & hook.match_rtype('has_apycot_environment')
    events = ('after_add_relation',)
    category = 'autoset'

    def __call__(self):
        project = self._cw.entity_from_eid(self.eidfrom)
        if not project.source_repository:
            projectenv = self._cw.entity_from_eid(self.eidto)
            SetSourceRepositoryOp(self._cw, project=project, projectenv=projectenv)


# set ticket 'in-progress' when attached to a patch ############################

class PatchLinkedToTicket(hook.Hook):
    __regid__ = 'trackervcs.patch-linked-to-ticket'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_ticket')
    events = ('after_add_relation',)
    category = 'autoset'

    def __call__(self):
        ticket = self._cw.entity_from_eid(self.eidto)
        ticket.cw_adapt_to('IWorkflowable').fire_transition_if_possible('start')


# attach patch to ticket on addition ###########################################

class PatchRevisionAdded(hook.Hook):
    __regid__ = 'trackervcs.patch-revision-added'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_revision', toetypes=('VersionContent',))
    events = ('after_add_relation',)
    category = 'autoset'

    def __call__(self):
        patch = self._cw.entity_from_eid(self.eidfrom)
        versioncontent = self._cw.entity_from_eid(self.eidto)
        patch_repo = versioncontent.repository
        source_repo = patch_repo.patchrepo_of
        for line in versioncontent.data.readlines():
            # skip mercurial metadata
            if line[0] == '#':
                continue
            # and stop at the end of the header
            if line[:4] == 'diff':
                break
            for eid in closed_eids(line):
                try:
                    rset = self._cw.execute(
                            'Any X WHERE X eid %(x)s, X concerns P, P source_repository R, R eid %(r)s',
                            {'x': typed_eid(eid), 'r': source_repo.eid})
                except TypeResolverException:
                    continue
                if rset:
                    ticket = rset.get_entity(0,0)
                    # XXX should we drop existing links first?
                    if all(x.eid != ticket.eid for x in patch.patch_ticket):
                        patch.set_relations(patch_ticket=ticket)

# security propagation #########################################################

# take care, code below may incidentally be propagated to nosylist.hooks.S_RELS
# depending on trackervcs/forge import order. Import order is fixed using
# __pkginfo__.__recommends__ so everything should be ok
tracker.S_RELS.add('source_repository')


# registration control #########################################################

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (RevisionAdded,
                                                     PatchLinkedToTicket,
                                                     PatchRevisionAdded,
                                                     ApycotEnvironmentAdded))
    if vreg.config['trusted-vcs-repositories']:
        vreg.register(RevisionAdded)

    if 'vcreview' in vreg.config.cubes():
        vreg.register(PatchLinkedToTicket)
        vreg.register(PatchRevisionAdded)
        # security propagation #################################################
        tracker.S_RELS |= set(('has_patch_repository', 'patch_revision',
                               'has_activity', ))
        tracker.O_RELS |= set(('patch_repository', 'point_of',))
    if 'apycot' in vreg.config.cubes():
        vreg.register(ApycotEnvironmentAdded)
