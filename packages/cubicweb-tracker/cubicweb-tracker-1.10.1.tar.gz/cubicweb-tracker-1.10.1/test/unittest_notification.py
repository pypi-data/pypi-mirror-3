"""tracker hooks tests"""
import re

from cubicweb.devtools.testlib import MAILBOX
from cubicweb.sobjects.notification import RenderAndSendNotificationView

from unittest_tracker import TrackerBaseTC


class NotificationTC(TrackerBaseTC):

    def test_notifications(self):
        p = self.create_project('hop').get_entity(0, 0)
        b = self.create_ticket('one more', pname='hop').get_entity(0, 0)
        b.set_attributes(priority=u'important')
        self.commit()
        self.assertEqual([re.sub('#\d+', '#EID', e.subject) for e in MAILBOX],
                          ['[data] New Project: hop',
                           '[hop] Ticket added: #EID one more',
                           ])
        self.assertEqual(MAILBOX[0].recipients, self.config['default-dest-addrs'])
        self.assertEqual(MAILBOX[1].recipients, self.config['default-dest-addrs'])
        # do some other changes
        MAILBOX[:] = ()
        b.set_attributes(priority=u'normal')
        b.cw_adapt_to('IWorkflowable').fire_transition('close')
        self.commit()
        self.assertEqual([re.sub('#\d+', '#EID', e.subject) for e in MAILBOX],
                          ['[hop] Ticket closed: #EID one more',
                           '[hop] Ticket updated: #EID one more',
                           ])
        self.assertEqual(MAILBOX[0].recipients, self.config['default-dest-addrs'])
        self.assertEqual(MAILBOX[1].recipients, self.config['default-dest-addrs'])


    def test_ticket_changes(self):
        v1 = self.create_version('0.0.1').get_entity(0, 0)
        v2 = self.create_version('0.0.2').get_entity(0, 0)
        self.commit()
        ticket = self.create_ticket('ticket').get_entity(0, 0)
        ticket.set_attributes(priority=u'minor')
        ticket.set_relations(appeared_in=v1)
        ticket.set_relations(done_in=v2)
        self.commit()
        self.assertEqual(len(MAILBOX), 1)
        self.assertEqual(MAILBOX[0].subject, '[cubicweb] Ticket added: #%s ticket' % ticket.eid)
        MAILBOX[:] = [] # reset mailbox
        # modify ticket, check notifications
        ticket.set_attributes(type=u'enhancement', description=u'huum',
                              priority=u'minor') # no actual priority change
        ticket.set_relations(done_in=None) # XXX not tracked
        self.assertEqual(len(MAILBOX), 0)
        self.commit()
        self.assertEqual(len(MAILBOX), 1)
        self.assertEqual(MAILBOX[0].subject, '[cubicweb] Ticket updated: #%s ticket' % ticket.eid)
        self.assertEqual(MAILBOX[0].content, '''
Ticket properties have been updated by admin:
* description updated
* type updated from "bug" to "enhancement"

url: http://testing.fr/cubicweb/ticket/%s
''' % ticket.eid)
        MAILBOX[:] = [] # reset mailbox
        # set version, change priority
        ticket.set_relations(done_in=v1, appeared_in=v2)
        ticket.set_attributes(priority=u'important')
        self.commit()
        self.assertEqual(len(MAILBOX), 1)
        self.assertEqual(MAILBOX[0].subject, '[cubicweb] Ticket updated: #%s ticket' % ticket.eid)
        self.assertEqual(MAILBOX[0].content, '''
Ticket properties have been updated by admin:
* done_in set to "0.0.1"
* priority updated from "minor" to "important"

url: http://testing.fr/cubicweb/ticket/%s
''' % ticket.eid)

    def test_version_changes(self):
        version = self.create_version('version').get_entity(0,0)
        self.commit()
        self.assertEqual(len(MAILBOX), 0)
        version.set_attributes(description=u'version description goes here')
        self.commit()
        # no notification when description is updated
        self.assertEqual(len(MAILBOX), 0)
        version.set_attributes(starting_date=u'01/01/01')
        self.commit()
        # notification for starting date changes
        self.assertEqual(len(MAILBOX), 1)
        version.set_attributes(prevision_date=u'01/01/01')
        self.commit()
        # notification for prevision date changes
        self.assertEqual(len(MAILBOX), 2)
        version.set_attributes(publication_date=u'01/01/01')
        self.commit()
        # notification for publication date changes
        self.assertEqual(len(MAILBOX), 3)

    def test_version_published(self):
        version = self.create_version('version').get_entity(0,0)
        self.commit()
        ticket = self.create_ticket('ticket bug').get_entity(0, 0)
        ticket.set_attributes(type=u'bug')
        self.execute('SET T done_in V WHERE T eid %(teid)s, V eid %(veid)s',
                     {'teid': ticket.eid, 'veid': version.eid})
        self.commit()
        enhancement = self.create_ticket('ticket enhancement').get_entity(0, 0)
        enhancement.set_attributes(type=u'enhancement')
        self.execute('SET T done_in V WHERE T eid %(teid)s, V eid %(veid)s',
                     {'teid': enhancement.eid, 'veid': version.eid})
        self.commit()
        task = self.create_ticket('ticket task').get_entity(0, 0)
        task.set_attributes(type=u'task')
        self.execute('SET T done_in V WHERE T eid %(teid)s, V eid %(veid)s',
                     {'teid': task.eid, 'veid': version.eid})
        self.commit()
        version.cw_adapt_to('IWorkflowable').fire_transition('start development')
        self.commit()

        MAILBOX[:] = [] # reset mailbox
        version.cw_adapt_to('IWorkflowable').fire_transition('publish')
        self.commit()
        self.assertEqual(len(MAILBOX), 1)
        self.assertEqual(MAILBOX[0].content, '''
Bugs fixed in this release:
\t- #%s %s

Enhancements implemented in this release:
\t- #%s %s

Tasks done in this release:
\t- #%s %s

url: http://testing.fr/cubicweb/project/cubicweb/%s
''' % (ticket.eid, ticket.title, enhancement.eid, enhancement.title, task.eid, task.title, version.num))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
