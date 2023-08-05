from cubicweb import devtools # set cubes package path
from cubes.tracker.testutils import TrackerBaseTC

class VersionTC(TrackerBaseTC):
    def setup_database(self):
        super(VersionTC, self).setup_database()
        self.v = self.create_version(u'0.0.0').get_entity(0, 0)

    def test_status_change_hook_create_testinstances(self):
        self.create_project('hop')
        ceid, = self.execute('INSERT Card C: C title "test card", C synopsis "test this", '
                             'C content "do thiss then that", C test_case_of P WHERE P name "cubicweb"')[0]
        self.execute('INSERT Card C: C title "test card2", C synopsis "test that", '
                     'C content "do that then this", C test_case_of P WHERE P name "hop"')[0]
        self.commit()
        iworkflowable = self.v.cw_adapt_to('IWorkflowable')
        iworkflowable.fire_transition('start development')
        self.commit()
        rset = self.execute('Any X,C WHERE X for_version V, X instance_of C, V eid %s' % self.v.eid)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.description[0], ('TestInstance', 'Card'))
        self.assertEqual(rset.rows[0][1], ceid)
        # check no interference with 'hop' project
        self.assertEqual(len(self.execute('TestInstance X')), 1)
        # test they are not copied twice when version get back to open then dev state
        iworkflowable.fire_transition('stop development')
        self.commit()
        iworkflowable.fire_transition('start development')
        self.commit()
        rset = self.execute('Any X,C WHERE X for_version V, X instance_of C, V eid %s' % self.v.eid)
        self.assertEqual(len(rset), 1)
        # test that if we delete the version, the test instance is deleted
        self.execute('DELETE Version V')
        self.commit()
        rset = self.execute('TestInstance X')
        self.assertEqual(len(rset), 0)

    def test_testinstance_created_if_version_in_dev(self):
        req = self.request()
        ticket = req.create_entity('Ticket', title=u'my ticket',
                                   concerns=self.v.version_of[0], done_in=self.v)
        iworkflowable = self.v.cw_adapt_to('IWorkflowable')
        iworkflowable.fire_transition('start development')
        self.commit()
        card = req.create_entity('Card', title=u'test card', content=u'just do it',
                                 test_case_for=ticket)
        rset = self.execute('Any X WHERE X is TestInstance, X for_version V, '
                            'X instance_of C, C eid %(c)s, V eid %(v)s',
                            {'c': card.eid, 'v': self.v.eid})
        self.failUnless(rset, 'the test instance was not created')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
