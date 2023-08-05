"""functional tests for default tracker security configuration"""
from cubicweb import Unauthorized, devtools # devtools import necessary before import from cubes.tracker
from cubes.tracker.testutils import SecurityTC, create_project_rql, create_ticket_rql, create_version_rql

# XXX cleanup by using TrackerTCMixIn with cw 3.6

class TrackerSecurityTC(SecurityTC):

    def test_base_security(self):
        # staff users should be able to insert/update project
        # but not "standard" users
        cnx = self.mylogin('staffuser')
        cu = cnx.cursor()
        # staff user insert
        cu.execute(*create_project_rql("myprojet"))
        cnx.commit() # OK
        # staff user update projects he doesn't own
        try:
            cu.execute('SET X name "mycubicweb" WHERE X is Project, X name "cubicweb"')
            cnx.commit()
        finally: # manual rollback
            cu.execute('SET X name "cubicweb" WHERE X is Project, X name "mycubicweb"')
            cnx.commit() # OK
        cnx = self.mylogin('stduser')
        cu = cnx.cursor()
        # standard user create
        cu.execute(*create_project_rql("mystdprojet"))
        self.assertRaises(Unauthorized, cnx.commit)
        cnx.rollback()
        # standard user try to update
        cu.execute('SET X name "cubicweb renamed" WHERE X is Project, X name "cubicweb"')
        self.assertRaises(Unauthorized, cnx.commit)
        cnx.rollback()
        # standard user with developer permission try to update
        self.grant_permission(self.session, self.cubicweb, 'users', u'developer')
        self.commit()
        cu.execute('SET X name "cubicweb renamed" WHERE X is Project, X name "cubicweb"')
        self.assertRaises(Unauthorized, cnx.commit)
        # standard user with client permission try to update
        self.grant_permission(self.session, self.cubicweb, 'users', u'client')
        self.commit()
        cu.execute('SET X name "cubicweb renamed" WHERE X is Project, X name "cubicweb"')
        self.assertRaises(Unauthorized, cnx.commit)
        cnx.rollback()


    def test_ticket_users_security(self):
        # standard user view/submit bug
        cnx = self.mylogin('stduser')
        cu = cnx.cursor()
        self.assertRaises(Unauthorized,
                          cu.execute, *create_ticket_rql('a ticket', 'cubicweb'))
        cnx.rollback()

    def test_ticket_staff_security(self):
        # staff users should be able to submit ticket on any project
        # but not "standard" users, and users in the cubicwebusers should
        # be able to submit ticket on the cubicweb project
        # staff user submit ticket
        cnx = self.mylogin('staffuser')
        cu = cnx.cursor()
        cu.execute(*create_ticket_rql('a bug', 'cubicweb')).get_entity(0, 0)
        cnx.commit() # OK

    def _test_ticket_with_cubicweb_local_role(self, cnx):
        # cubicweb client/developper user submit ticket
        cu = cnx.cursor()
        ticket = cu.execute(*create_ticket_rql('a ticket', 'cubicweb')).get_entity(0, 0)
        cnx.commit() # OK
        self.assertRaises(Unauthorized,
                          cu.execute, *create_ticket_rql('a ticket', 'project2'))
        cnx.rollback()
        # same thing but using multiple queries
        beid = cu.execute('INSERT Ticket X: X title %(title)s', {'title': u'another ticket'})[0][0]
        cu.execute('SET X concerns P WHERE P name %(name)s, X eid %(x)s',
                   {'x': beid, 'name': 'cubicweb'})
        cnx.commit() # OK

    def test_ticket_developper_security(self):
        # cubicweb developer user submit ticket
        cnx = self.mylogin('prj1developer')
        self._test_ticket_with_cubicweb_local_role(cnx)

    def test_ticket_client_security(self):
        # cubicweb client user submit ticket
        cnx = self.mylogin('prj1client')
        # XXX FAILS
        self._test_ticket_with_cubicweb_local_role(cnx)

    def test_ticket_workflow(self):
        beid = self.execute(*create_ticket_rql('a ticket', 'cubicweb'))[0][0]
        self.commit() # to set initial state properly
        # test ticket's workflow
        # client can't any more modify their ticket once no more in the created state,
        # though staff/developper can
        cnx = self.login('staffuser')
        cu = cnx.cursor()
        cu.execute('SET X description "bla" WHERE X eid %(x)s', {'x': beid})
        cnx.commit() # OK
        cnx = self.login('prj1developer')
        cu = cnx.cursor()
        cu.execute('SET X description "bla bla" WHERE X eid %(x)s', {'x': beid})
        cnx.commit() # OK
        # only staff/developer can pass the start transition
        self._test_tr_fail('prj1client', beid, 'start')
        self._test_tr_success('prj1developer', beid, 'start')
        # client can not modify ticket in-progress
        cnx = self.login('prj1client')
        cu = cnx.cursor()
        cu.execute('SET X description "bla bla bla" WHERE X eid %(x)s', {'x': beid})
        self.assertRaises(Unauthorized, cnx.commit)
        # only staff/developper can pass the close transition
        self._test_tr_fail('prj1client', beid, 'close')
        self._test_tr_success('prj1developer', beid, 'close')


    def test_version_security(self):
        # staff users should be able to create version on any project
        # but not "standard" users, and users in the cubicwebclients should
        # be able to create version on the cubicweb project
        # staff user create version
        cnx = self.mylogin('staffuser')
        cu = cnx.cursor()
        cu.execute(*create_version_rql('0.1.2', 'cubicweb'))
        cnx.commit() # OK
        # standard user create version
        cnx = self.login('stduser')
        cu = cnx.cursor()
        self.assertRaises(Unauthorized,
                          cu.execute, *create_version_rql('0.1.3', 'cubicweb'))
        cnx.rollback()
        # cubicweb user create version
        cnx = self.mylogin('prj1developer')
        cu = cnx.cursor()
        self.assertRaises(Unauthorized, cu.execute, *create_version_rql('0.1.3', 'cubicweb'))
        cnx.rollback()
        # cubicwebclients user create version
        cnx = self.mylogin('prj1client')
        cu = cnx.cursor()
        cu.execute(*create_version_rql('0.1.3', 'cubicweb'))
        cnx.commit() # OK
        self.assertRaises(Unauthorized,
                          cu.execute, *create_version_rql('0.1.4', 'project2'))
        cnx.rollback()


    def test_ticket_done_in_security(self):
        cnx = self.mylogin('staffuser')
        cu = cnx.cursor()
        self.assertTrue(cu.execute('Any X WHERE X is Project, X name "cubicweb"'))
        veid1 = cu.execute(*create_version_rql('0.1.2', 'cubicweb'))[0][0]
        veid2 = cu.execute(*create_version_rql('0.2.0', 'cubicweb'))[0][0]
        x = cu.execute(*create_ticket_rql('blabla', 'cubicweb'))[0][0]
        cnx.commit()
        # cubicweb user affect ticket to version in planned state
        cnx = self.mylogin('prj1developer')
        cu = cnx.cursor()
        cu.execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid1})
        cnx.commit()
        cu.execute('DELETE X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid1})
        cnx.commit()
        # cubicweb client affect ticket to version in planned state
        cnx = self.mylogin('prj1client')
        cu = cnx.cursor()
        trset = cu.execute('Any X WHERE X eid %(x)s', {'x': x})
        # # XXX test move to next version is there
        # actdict = self.vreg['actions'].possible_actions(self.request(), rset=rset)
        # assert actdict is None, actdict
        cu.execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid1})
        cnx.commit()
        # cubicweb user change ticket's version, then remove it from version
        cnx = self.mylogin('prj1developer')
        cu = cnx.cursor()
        cu.execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid2})
        cnx.commit()
        cu.execute('DELETE X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid2})
        cnx.commit()
        # cubicweb client change ticket's version in planned state
        cnx = self.mylogin('prj1client')
        cu = cnx.cursor()
        cu.execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid2})
        cnx.commit()
        # cubicweb client remove ticket from version in planned state
        cu.execute('DELETE X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid2})
        cnx.commit()
        # prepare version using admin connection
        cnx = self.mylogin('admin')
        cu = cnx.cursor()
        x2 = cu.execute(*create_ticket_rql('blibli', 'cubicweb'))[0][0]
        cu.execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                   {'x': x, 'v': veid1})
        v1 = cu.execute('Any X WHERE X eid %(x)s', {'x': veid1}).get_entity(0, 0)
        v1.cw_adapt_to('IWorkflowable').fire_transition('start development')
        cnx.commit()
        cnx = self.mylogin('prj1client')
        cu = cnx.cursor()
        # cubicweb client remove ticket from version in dev state
        self.assertRaises(Unauthorized, cu.execute,
                          'DELETE X done_in V WHERE X eid %(x)s, V eid %(v)s',
                          {'x': x, 'v': veid1})
        # cubicweb client change ticket's version
        self.assertRaises(Unauthorized, cu.execute,
                          'SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                          {'x': x, 'v': veid2})
        # cubicweb client affect ticket to version in dev state
        self.assertRaises(Unauthorized, cu.execute,
                          'SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                          {'x': x2, 'v': veid1})
        cnx.rollback()

    def test_has_group_permission_sync(self):
        # delete user from group
        self.execute('DELETE U in_group G WHERE U login "prj1client", G name "cubicwebclients"')
        cachedperms = self.execute('Any UL, PN WHERE U has_group_permission P, U login UL, P label PN')
        self.assertEqual(len(cachedperms), 3, cachedperms.rows)
        self.assertNotIn('prj1client', dict(cachedperms))
        # set user in group
        self.execute('SET U in_group G WHERE U login "prj1client", G name "project2clients"')
        cachedperms = self.execute('Any UL, PN WHERE U has_group_permission P, U login UL, P label PN')
        self.assertEqual(len(cachedperms), 4, cachedperms.rows)
        self.assertIn('prj1client', dict(cachedperms))
        self.assertEqual(dict(cachedperms)['prj1client'], 'project2clients')


        expected_perm = [('prj1client', 'cubicwebclients'),
                         ('prj1client', 'project2clients'),
                         ('prj2client', 'cubicwebclients'),
                         ('prj2client', 'project2clients'),
                         ('prj1developer', 'cubicwebdevelopers'),
                         ('prj2developer', 'project2developers'),]

                        #[['prj1client', 'cubicwebclients'],
                        # ['prj1client', 'projet2clients'],
                        # ['prj1developer', 'cubicwebdevelopers'],])

        for rql in (
                # set required group to permission
                'SET P require_group G WHERE P label "cubicwebclients",'
                '                    G name "project2clients"',
                # set user in group giving already granted permission
                'SET U in_group G WHERE U login "prj1client",'
                '               G name "cubicwebclients"',
                # set required group to already given permission
                'SET P require_group G WHERE P label "project2clients",'
                '                    G name "cubicwebclients"',
                # remove a permission's group
                # but permission still granted by another group
                'DELETE P require_group G WHERE P label "project2clients",'
                '                       G name "cubicwebclients"',
                # delete user from a group
                # but permission still granted by another group
                'DELETE U in_group G WHERE U login "prj1client",'
                '                  G name "cubicwebclients"',
            ):
            self.execute(rql)
            cachedperms = self.execute('Any UL, PN '
                                       'WHERE U has_group_permission P,'
                                       '      U login UL, P label PN')
            cachedperms = (tuple(i) for i in cachedperms.rows)
            self.assertItemsEqual( cachedperms , expected_perm)
        # delete required group from permission
        self.execute('DELETE P require_group G WHERE P label "cubicwebclients", G name "project2clients"')
        cachedperms = self.execute('Any UL, PN WHERE U has_group_permission P, U login UL, P label PN')
        cachedperms = (tuple(i) for i in cachedperms.rows)
        self.assertItemsEqual(cachedperms,
                          [('prj1client',     'project2clients'),
                           ('prj1developer',  'cubicwebdevelopers'),
                           ('prj2client',    'project2clients'),
                           ('prj2developer', 'project2developers'), ])


    def test_ticket_creation_form_done_in_vocab(self):
        v1 = self.create_version('0.0.1').get_entity(0, 0)
        v2 = self.create_version('0.1.0').get_entity(0, 0)
        v3 = self.create_version('0.2.0').get_entity(0, 0)
        v4 = self.create_version('0.3.0').get_entity(0, 0)
        self.commit()
        v1.cw_adapt_to('IWorkflowable').fire_transition('start development')
        v1.cw_adapt_to('IWorkflowable').fire_transition('publish')
        v2.cw_adapt_to('IWorkflowable').fire_transition('start development')
        v2.cw_adapt_to('IWorkflowable').fire_transition('ready')
        v3.cw_adapt_to('IWorkflowable').fire_transition('start development')
        self.commit()
        req = self.request()
        req.form['__linkto'] = 'concerns:%s:subject' % self.cubicweb.eid
        ticket = self.vreg['etypes'].etype_class('Ticket')(req)
        form = self.vreg['forms'].select('edition', req, entity=ticket)
        field = form.field_by_name('done_in', 'subject')
        self.assertEqual(field.choices(form, field),
                          [('', '__cubicweb_internal_field__'),
                           ('cubicweb 0.1.0', unicode(v2.eid)),
                           ('cubicweb 0.2.0', unicode(v3.eid)),
                           ('cubicweb 0.3.0', unicode(v4.eid))])
        cnx = self.login('prj1client')
        req = self.request(__linkto='concerns:%s:subject' % self.cubicweb.eid)
        ticket = self.vreg['etypes'].etype_class('Ticket')(req)
        form = self.vreg['forms'].select('edition', req, entity=ticket)
        field = form.field_by_name('done_in', 'subject')
        self.assertEqual(field.choices(form, field),
                          [('', '__cubicweb_internal_field__'),
                           ('cubicweb 0.3.0', unicode(v4.eid))])


    def test_nonregr_done_in_unrelated(self):
        cnx = self.login('prj1client')
        ticket = self.vreg['etypes'].etype_class('Ticket')(cnx.request())
        ticket.unrelated('done_in', 'Version')


    def test_movetonext_not_appears(self):
        """test movetonext properly check user actually can move the ticket,
        e.g. has permission to delete it from its current version and to add it
        to the new version.
        """
        v1 = self.create_version('0.0.1').get_entity(0, 0)
        v2 = self.create_version('0.0.2').get_entity(0, 0)
        t1 = self.create_ticket('hop', '0.0.1').get_entity(0, 0)
        self.commit()
        cnx = self.mylogin('prj1client')
        req = cnx.request()
        rset = req.execute('Any X WHERE X eid %(x)s', {'x': t1.eid})
        self.assertTrue(req.vreg['actions'].select_or_none('movetonext', req, rset=rset))
        v1.cw_adapt_to('IWorkflowable').change_state('dev')
        self._orig_cnx[0].commit()
        req = cnx.request()
        rset = req.execute('Any X WHERE X eid %(x)s', {'x': t1.eid})
        self.assertFalse(req.vreg['actions'].select_or_none('movetonext', req, rset=rset))
        v1.cw_adapt_to('IWorkflowable').change_state('planned')
        v2.cw_adapt_to('IWorkflowable').change_state('dev')
        self._orig_cnx[0].commit()
        req = cnx.request()
        rset = req.execute('Any X WHERE X eid %(x)s', {'x': t1.eid})
        self.assertFalse(req.vreg['actions'].select_or_none('movetonext', req, rset=rset))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
