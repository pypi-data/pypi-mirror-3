"""Tracker unit tests"""
from __future__ import with_statement

from datetime import datetime, timedelta

from logilab.common.testlib import unittest_main, mock_object

from cubicweb import Unauthorized, ValidationError
from cubicweb.utils import transitive_closure_of
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web import INTERNAL_FIELD_VALUE
from cubicweb.web.views import actions, workflow
from cubicweb.server.session import security_enabled

from cubes.tracker.views import version, ticket, document, forms
from cubes.tracker.testutils import TrackerTCMixIn, TrackerBaseTC

ONEDAY = timedelta(1)


class TrackerTests(TrackerBaseTC):
    """test tracker specific behaviours"""

    def test_schema(self):
        seealso = self.schema['see_also']
        self.assert_('Ticket' in seealso.subjects(), seealso.subjects())

    def test_ticket_sync_identical(self):
        veid, = self.create_version(u'0.0.0')[0]
        t1 = self.create_ticket('ticket').get_entity(0, 0)
        t2 = self.create_ticket('identical ticket').get_entity(0, 0)
        self.execute('SET X identical_to O WHERE X eid %(x)s, O eid %(o)s',
                     {'x':t1.eid, 'o':t2.eid})
        self.commit()
        t1.cw_adapt_to('IWorkflowable').fire_transition('close')
        self.commit()
        t2.cw_clear_all_caches()
        self.assertEqual(t2.cw_adapt_to('IWorkflowable').state, 'closed')
        self.execute('SET X done_in V WHERE X eid %(x)s, V is Version',
                     {'x':t1.eid})
        self.assertEqual(t2.done_in[0].eid, veid)
        self.commit()


class ProjectTC(TrackerBaseTC):
    """Project"""

    def test_versions_in_state(self):
        v1 = self.create_version(u'0.0.0').get_entity(0, 0)
        v2 = self.create_version(u'0.1.0').get_entity(0, 0)
        self.commit()
        v1.cw_adapt_to('IWorkflowable').fire_transition('start development')
        vrset = self.cubicweb.versions_in_state(('planned', 'dev'))
        self.assertEqual(len(vrset), 2)
        self.assertEqual(vrset[0][0], v1.eid)
        self.assertEqual(vrset[1][0], v2.eid)
        vrset = self.cubicweb.versions_in_state(('planned',))
        self.assertEqual(len(vrset), 1)
        self.assertEqual(vrset[0][0], v2.eid)

    def test_possible_actions(self):
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.commit()
        self.assertListEqual(self.pactions(req, rset),
                              [('edit', actions.ModifyAction),
                               ('managepermission', actions.ManagePermissionsAction),
                               ('addrelated', actions.AddRelatedActions),
                               ('delete', actions.DeleteAction),
                               ('copy', actions.CopyAction),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [(u'add Project subproject_of Project object',
                                u'http://testing.fr/cubicweb/add/Project?__linkto=subproject_of%%3A%s%%3Asubject&__redirectpath=project%%2Fcubicweb&__redirectvid=' % self.cubicweb.eid),
                               (u'add Ticket concerns Project object',
                                u'http://testing.fr/cubicweb/add/Ticket?__linkto=concerns%%3A%s%%3Asubject&__redirectpath=project%%2Fcubicweb&__redirectvid=' % self.cubicweb.eid),
                               (u'add Version version_of Project object',
                                u'http://testing.fr/cubicweb/add/Version?__linkto=version_of%%3A%s%%3Asubject&__redirectpath=project%%2Fcubicweb&__redirectvid=' % self.cubicweb.eid)])
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                              [('addrelated', actions.AddRelatedActions),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])

    def test_versions_order(self):
        veid1, = self.create_version(u'0.0.0')[0]
        veid2, = self.create_version(u'0.1.0')[0]
        veid3, = self.create_version(u'0.0.1')[0]
        self.assertEqual([v.eid for v in self.cubicweb.reverse_version_of],
                          [veid2, veid3, veid1])



class VersionTC(TrackerBaseTC):
    """Version"""
    def setup_database(self):
        super(VersionTC, self).setup_database()
        self.v = self.create_version(u'0.0.0').get_entity(0, 0)
        self.t1 = self.create_ticket(u"enchancement1", u'0.0.0').get_entity(0, 0)

    def _test_anon_actions(self, with_hist=True):
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('addrelated', actions.AddRelatedActions),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        if with_hist:
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                  [(u'view history', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?vid=wfhistory')])
        else:
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                  [])

    def test_possible_actions_and_transitions(self):
        req = self.request()
        req.create_entity('CWGroup', name=u'totogroup')
        self.create_user(req, 'toto', ('users', 'totogroup'))
        self.grant_permission(self.session, self.cubicweb, 'totogroup', 'client', 'soumettre sur cubicweb')
        self.commit()
        # one planned version
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        wf = self.v.cw_adapt_to('IWorkflowable').current_workflow
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('edit', actions.ModifyAction),
                               ('managepermission', actions.ManagePermissionsAction),
                               ('addrelated', actions.AddRelatedActions),
                               ('delete', actions.DeleteAction),
                               ('copy', actions.CopyAction),
                               ('addticket', version.VersionAddTicketAction),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'start development', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?treid=%s&vid=statuschange' %
                                wf.transition_by_name('start development').eid),
                               (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)])
        self.login('toto') #####################################################
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('edit', actions.ModifyAction),
                               ('addrelated', actions.AddRelatedActions),
                               ('copy', actions.CopyAction),
                               ('addticket', version.VersionAddTicketAction),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [])
        self._test_anon_actions(False) #########################################
        self.restore_connection() ##############################################
        # one in dev version
        self.v.cw_adapt_to('IWorkflowable').fire_transition('start development')
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('addticket', version.VersionAddTicketAction),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'ready', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?treid=%s&vid=statuschange' %
                                wf.transition_by_name('ready').eid),
                               (u'publish', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?treid=%s&vid=statuschange' %
                                wf.transition_by_name('publish').eid),
                               (u'stop development', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?treid=%s&vid=statuschange' %
                                wf.transition_by_name('stop development').eid),
                               (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid),
                               (u'view history', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?vid=wfhistory')])
        self.login('toto') #####################################################
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('edit', actions.ModifyAction),
                               ('addrelated', actions.AddRelatedActions),
                               ('copy', actions.CopyAction),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'view history', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?vid=wfhistory')])
        self._test_anon_actions() ##############################################
        self.restore_connection() ##############################################
        # one in ready version
        self.v.cw_adapt_to('IWorkflowable').fire_transition('ready')
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'publish', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?treid=%s&vid=statuschange' %
                                wf.transition_by_name('publish').eid),
                               (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s' % wf.eid),
                               (u'view history', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?vid=wfhistory')])
        self.login('toto') #####################################################
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('edit', actions.ModifyAction),
                               ('addrelated', actions.AddRelatedActions),
                               ('copy', actions.CopyAction),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'view history', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?vid=wfhistory')])
        self._test_anon_actions() ##############################################
        self.restore_connection() ##############################################
        # one in published version
        self.v.cw_adapt_to('IWorkflowable').fire_transition('publish')
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('edit', actions.ModifyAction),
                               ('managepermission', actions.ManagePermissionsAction),
                               ('addrelated', actions.AddRelatedActions),
                               ('delete', actions.DeleteAction),
                               ('copy', actions.CopyAction),
                               ('submitbug', version.VersionSubmitBugAction),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'view history', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?vid=wfhistory')])
        self.login('toto') #####################################################
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('edit', actions.ModifyAction),
                               ('addrelated', actions.AddRelatedActions),
                               ('copy', actions.CopyAction),
                               ('submitbug', version.VersionSubmitBugAction),
                               ('pvrestexport', document.ProjectVersionExportAction),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'view history', u'http://testing.fr/cubicweb/project/cubicweb/0.0.0?vid=wfhistory')])
        self._test_anon_actions() ##############################################

    def test_ticket_status_change_vp_start_version(self):
        self.t1.cw_adapt_to('IWorkflowable').fire_transition('start')
        self.commit()
        self.v.cw_clear_all_caches()
        self.assertEqual(self.v.cw_adapt_to('IWorkflowable').state, 'dev')

    def test_next_version(self):
        v2 = self.create_version("0.0.1").get_entity(0, 0)
        self.commit()
        self.assertEqual(self.v.next_version().num, v2.num)
        self.assertEqual(self.v.next_version(('dev',)), None)
        self.assertEqual(v2.next_version(), None)

    def test_duplicated_version(self):
        with self.assertRaises(ValidationError) as cm:
            self.create_version(u'0.0.0')
        self.assertEqual(cm.exception.errors,
                         {'num': u'version 0.0.0 already exists for project cubicweb',
                          'version_of': u'version 0.0.0 already exists for project cubicweb'})

    def test_status_change_form(self):
        req = self.request()
        rset = req.execute('Any X WHERE X is Version')
        tr = req.execute('Transition X WHERE X name "start development"').get_entity(0, 0)
        form = self.vreg['forms'].select('changestate', req, transition=tr,
                                         rset=rset, row=0, col=0)
        self.assertEqual(form.__class__, workflow.ChangeStateForm)
        tr = req.execute('Transition X WHERE X name "publish"').get_entity(0, 0)
        form = self.vreg['forms'].select('changestate', req, transition=tr,
                                         rset=rset, row=0, col=0)
        self.assertEqual(form.__class__, forms.VersionChangeStateForm)


class TicketTC(TrackerBaseTC):
    """Ticket"""

    def setup_database(self):
        super(TicketTC, self).setup_database()
        self.v = self.create_version(u'0.0.0').get_entity(0, 0)
        self.t1 = self.create_ticket(u"enhancement1").get_entity(0, 0)

    def test_modification_date_after_state_changed(self):
        olddate = datetime.today() - ONEDAY
        self.t1.set_attributes(modification_date=olddate)
        self.t1.cw_adapt_to('IWorkflowable').fire_transition('start')
        self.commit()
        self.assertModificationDateGreater(self.t1, olddate)

    def test_possible_actions_and_transitions(self):
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('movetonext', ticket.TicketMoveToNextVersionActions),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        wf = self.t1.cw_adapt_to('IWorkflowable').current_workflow
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'start',
                                u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                (self.t1.eid, wf.transition_by_name('start').eid)),
                               (u'close',
                                u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                (self.t1.eid, wf.transition_by_name('close').eid)),
                               (u'view workflow',
                                u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)])
        self.login('anon') #####################################################
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('addrelated', actions.AddRelatedActions),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [])
        self.restore_connection() ##############################################
        self.t1.cw_adapt_to('IWorkflowable').fire_transition('start')
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('movetonext', ticket.TicketMoveToNextVersionActions),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'close',
                                u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                (self.t1.eid, wf.transition_by_name('close').eid)),
                               (u'view workflow',
                                u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid),
                               (u'view history',
                                u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])
        self.login('anon') #####################################################
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('addrelated', actions.AddRelatedActions),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])
        self.restore_connection() ##############################################
        self.t1.cw_adapt_to('IWorkflowable').fire_transition('close')
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])
        self.login('anon') #####################################################
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                              [('workflow', workflow.WorkflowActions),
                               ('addrelated', actions.AddRelatedActions),
                               ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                              [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])

    def test_nonregr_anon_move_ticket(self):
        self.login('anon')
        rql = 'SET X done_in V WHERE X eid %s, V eid %s' % (self.t1.eid, self.v.eid)
        self.assertRaises(Unauthorized, self.execute, rql)

    def test_nonregr_ticket_breadcrumbs(self):
        bcrumbs = [x.eid for x in self.t1.cw_adapt_to('IBreadCrumbs').breadcrumbs()]
        self.assertEqual(bcrumbs, [self.t1.project.eid, self.t1.eid])
        view = mock_object(__regid__='primary')
        bcrumbs = [x.eid for x in self.t1.cw_adapt_to('IBreadCrumbs').breadcrumbs(view)]
        self.assertEqual(bcrumbs, [self.t1.project.eid, self.t1.eid])


class CreationTC(TrackerBaseTC):

    def test_non_regr_version_creation(self):
        req = self.request(**{
            'eid' : 'A',
            '__type:A':  'Version',
            '__maineid':  'A',
            #
            '__linkto' : 'version_of:%s:subject' % self.cubicweb.eid,
            # num
            '_cw_entity_fields:A' : 'num-subject',
            'num-subject:A' : u"3.0",
            # explicit redirect path
            '__redirectpath' : '/project/cubicweb',
            })
        path, _params = self.expect_redirect_publish(req)
        self.assertEqual(path, '/project/cubicweb')
        rset = self.execute('Any N WHERE V num N, V version_of P, P eid %s' % self.cubicweb.eid)
        self.assertTrue(len(rset) == 1)
        self.assertEqual(rset[0][0], u"3.0")


class SubProjectTC(CubicWebTC):

    tickets_wf_map = {'created' : 'created',
                      'closed' : 'closed'}
    tickets_tr_map = {'start' : 'start',
                      'close' : 'close'}

    versions_wf_map = {'created'    : 'planned',
                       'inprogress' : 'dev',
                       'released'   : 'published'}
    versions_tr_map = {'start' : 'start development',
                       'release'  : 'publish',
                       'stop' : 'stop development'}

    def setup_database(self):
        self.setup_projects()

    def setup_projects(self):
        req = self.request()
        projects = (u'Comet', u'Tracker', u'Lgc')
        for proj in projects:
            setattr(self, proj.lower(), req.create_entity('Project', name=proj))
        self.doc = req.create_entity('Project', name=u'Comet documentation')
        self.userdoc = req.create_entity('Project', name=u'User manual')
        self.devdoc = req.create_entity('Project', name=u'Developper manual')
        for parent, child in ((u'Comet', u'Tracker'),
                              (u'Tracker', u'Lgc'),
                              (u'Comet', u'Comet documentation'),
                              (u'Comet documentation', u'User manual'),
                              (u'Comet documentation', u'Developper manual')):
            assert self.execute('SET P subproject_of R WHERE R name %(r)s, P name %(p)s',
                         {'r' : parent, 'p' : child})
        self.commit()
        return projects
        # And now, for something completely diffent

    def change_state(self, entity, statename):
        with security_enabled(self.session, False, False):
            self.session.execute('DELETE X in_state S WHERE X eid %(x)s',
                                 {'x': entity.eid})
            self.session.execute('SET X in_state S WHERE S name %(state)s, X eid %(x)s',
                                 {'state': statename, 'x': entity.eid})

    def setup_versions(self):
        req = self.request()
        versions = []
        for proj in reversed(tuple(transitive_closure_of(self.comet, 'reverse_subproject_of'))):
            ver = req.create_entity('Version', num=u'0.1.0')
            versions.append(ver.eid)
            self.execute('SET V version_of P WHERE V eid %(v)s, P eid %(p)s',
                         {'v' : ver.eid, 'p' : proj.eid})
            self.execute('SET V1 depends_on V2 WHERE V1 eid %(v)s, V2 version_of P2, '
                         'P2 subproject_of P1, P1 eid %(p)s, V2 num %(num)s',
                         {'v': ver.eid, 'p': proj.eid, 'num': '0.1.0'})
            self.commit()
            self.change_state(ver, self.versions_wf_map['released'])
            ver = req.create_entity('Version', num=u'0.2.0')
            self.execute('SET V version_of P WHERE V eid %(v)s, P eid %(p)s',
                         {'v' : ver.eid, 'p' : proj.eid})
            self.execute('SET V1 depends_on V2 WHERE V1 eid %(v)s, V2 version_of P2, '
                         'P2 subproject_of P1, P1 eid %(p)s, V2 num %(num)s',
                         {'v': ver.eid, 'p': proj.eid, 'num': '0.2.0'})
            self.commit()
            self.change_state(ver, self.versions_wf_map['inprogress'])
            ver = req.create_entity('Version', num=u'0.3.0')
            self.execute('SET V version_of P WHERE V eid %(v)s, P eid %(p)s',
                         {'v' : ver.eid, 'p' : proj.eid})
            self.execute('SET V1 depends_on V2 WHERE V1 eid %(v)s, V2 version_of P2, '
                         'P2 subproject_of P1, P1 eid %(p)s, V2 num %(num)s',
                         {'v': ver.eid, 'p': proj.eid, 'num': '0.3.0'})
            self.commit()
        # set dependency between all versions (in the same state) of the tree
        self.commit()
        return versions

    def setup_tickets(self):
        """create a bunch of tickets for different projects, all in version 0.2.0
        """
        req = self.request()
        for title, ttype, pname in ((u'add support for xhtml -> pdf conversion', u'enhancement', u'Lgc'),
                                    (u'extract core from forge cube', u'enhancement', u'Tracker'),
                                    (u'add comet-specific attributes/relations', u'enhancement', u'Comet'),
                                    (u'write a tutorial', u'enhancement', u'User manual'),
                                    (u'detail a bit configuration steps', u'enhancement', u'Developper manual')):
            t = req.create_entity('Ticket', title=title, type=ttype)
            self.execute('SET T concerns P, T done_in V '
                         'WHERE T eid %(t)s, P name %(p)s, V num "0.2.0", V version_of P',
                         {'t' : t.eid, 'p' : pname})
        self.commit()
        for ticket in self.userdoc.reverse_concerns + self.lgc.reverse_concerns:
            ticket.cw_adapt_to('IWorkflowable').change_state(self.tickets_wf_map['closed'])
        self.commit()
        for ver in self.userdoc.reverse_version_of + self.lgc.reverse_version_of:
            ver.cw_adapt_to('IWorkflowable').change_state(self.versions_wf_map['released'])
        self.commit()

    def test_deps_order(self):
        comet_children_eids = set(p.eid for p in transitive_closure_of(
            self.comet, 'reverse_subproject_of'))
        self.assertEqual(len(comet_children_eids), 6)
        self.assertTrue(self.doc.eid in comet_children_eids)
        tracker_children = list(transitive_closure_of(self.tracker, 'reverse_subproject_of'))
        self.assertEqual(len(tracker_children), 2)

    def test_loop_safety_belt(self):
        self.assertRaises(ValidationError, self.execute,
                          'SET P2 subproject_of P1 WHERE P1 eid %(p1)s, P2 eid %(p2)s',
                          {'p1' : self.devdoc.eid, 'p2' : self.comet.eid})

    def test_tree(self):
        for proj, rootp, leafp in (('comet', True, False),
                                   ('doc', False, False),
                                   ('userdoc', False, True),
                                   ('devdoc', False, True),
                                   ('tracker', False, False),
                                   ('lgc', False, True)):
            proj = getattr(self, proj)
            self.assertEqual(proj.cw_adapt_to('ITree').is_root(), rootp)
            self.assertEqual(proj.cw_adapt_to('ITree').is_leaf(), leafp)

    def test_tickets(self):
        self.setup_versions()
        self.setup_tickets()
        self.assertEqual(len(self.lgc.reverse_concerns), 1)
        self.assertEqual(self.execute('Any COUNT(T) WHERE T done_in V, V in_state S, S name "%s"'
                                       % self.versions_wf_map['inprogress']).rows[0][0],
                          3)

if __name__ == '__main__':
    unittest_main()
