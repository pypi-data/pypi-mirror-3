from itertools import chain

from cubicweb.selectors import is_instance
from cubicweb.server import hook

class MakeTestInstancesOnVersionStatusChange(hook.Hook):
    """when a Version is going from 'planned' to 'in development', search
    for related test cards and create a test instance for each of them
    """
    __regid__ = 'createtestinstances'
    __select__ = hook.Hook.__select__ & is_instance('TrInfo')
    events = ('after_add_entity',)

    def __call__(self):
        forentity = self.entity.for_entity
        if forentity.e_schema  != 'Version':
            return
        if self.entity.new_state.name == 'dev':
            self.copy_cards(forentity.eid)

    def copy_cards(self, veid):
        # get cards for past stories
        rset1 = self._cw.execute('Any X,XT WHERE X test_case_of P, X test_case_for S, S in_state ST,'
                                'ST name "done", V version_of P, V eid %(v)s, X title XT,'
                                'NOT EXISTS(TI instance_of X, TI for_version V)',
                               {'v': veid})
        # get cards for stories in this version
        rset2 = self._cw.execute('Any X,XT WHERE X test_case_of P, X test_case_for S,'
                                'S done_in V, V eid %(v)s, X title XT,'
                                'NOT EXISTS(TI instance_of X, TI for_version V)',
                               {'v': veid})
        # get general cards (not related to a particular story
        rset3 = self._cw.execute('Any X,XT WHERE X test_case_of P, NOT X test_case_for S,'
                                'V version_of P, V eid %(v)s, X title XT,'
                                'NOT EXISTS(TI instance_of X, TI for_version V)',
                               {'v': veid})
        done = set()
        for eid, title in chain(rset1, rset2, rset3):
            if eid in done:
                continue
            done.add(eid)
            self._cw.execute('INSERT TestInstance X: X name %(name)s,'
                             'X instance_of C, X for_version V '
                             'WHERE C eid %(c)s, V eid %(v)s',
                             {'v': veid, 'c': eid, 'name': title})


class CreateTestInstanceOnNewTestCard(hook.Hook):
    """create a TestInstance automatically when a test card is added on
    a version already in development.
    """
    __regid__ = 'testcard.create-testinstance'
    __select__ = hook.Hook.__select__ & hook.match_rtype('test_case_for')
    events = ('after_add_relation',)

    def __call__(self):
        req = self._cw
        ticket = req.entity_from_eid(self.eidto)
        card = req.entity_from_eid(self.eidfrom)
        if ticket.done_in:
            version = ticket.done_in[0]
            state = version.cw_adapt_to('IWorkflowable').state
            if state == 'dev':
                req.create_entity('TestInstance', name=card.title,
                                  for_version=version, instance_of=card)

