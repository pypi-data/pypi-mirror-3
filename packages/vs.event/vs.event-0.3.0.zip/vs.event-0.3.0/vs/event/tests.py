################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Walther
################################################################

from dateable import kalends
import datetime
from dateutil import rrule

import zope.interface
from Testing import ZopeTestCase
from Products.Five import zcml, fiveconfigure 
from AccessControl import getSecurityManager
from DateTime.DateTime import DateTime
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.layer import onsetup

from vs.event.content import event_util

PloneTestCase.installProduct('vs.event')

@onsetup
def setup_package():
    fiveconfigure.debug_mode = True
    import dateable.chronos
    import vs.event
    zcml.load_config('configure.zcml', dateable.chronos)
    zcml.load_config('configure.zcml', vs.event)
    fiveconfigure.debug_mode = False
    ZopeTestCase.installPackage('dateable.chronos')
    ZopeTestCase.installPackage('vs.event')

setup_package()
PloneTestCase.setupPloneSite(products=('vs.event', 'dateable.chronos'))

class TestBase(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        ZopeTestCase.utils.setupCoreSessions(self.app)
        self.membership = self.portal.portal_membership
        self.membership.addMember('god', 'secret', ['Manager'], [])

class VSEventTest(TestBase):

    def testCalendarToolCheck(self):
        pc = self.portal.portal_calendar
        self.assertEqual(pc.meta_type, 'Chronos Calendar Tool')

    def testProperties(self):
        pc = self.portal.portal_calendar
        self.assertEqual(pc.vs_event_supplementary_events, True)
        self.assertEqual('VSEvent' in pc.getCalendarTypes(), True)
        self.assertEqual('VSSubEvent' in pc.getCalendarTypes(), True)

    def testCreateEvent(self):
        self.login('god')
        user = getSecurityManager().getUser()
        self.assertEqual('Manager' in user.getRoles(), True)
        self.portal.invokeFactory('VSEvent', id='foo')
        event = self.portal['foo']
        self.assertEqual(event.portal_type, 'VSEvent') 

    def testOneDayEvent(self):
        self.login('god')
        self.portal.invokeFactory('VSEvent', id='foo')
        event = self.portal['foo']
        event.setStartDate(DateTime(2009, 01, 01))
        event.setEndDate(DateTime(2009, 01, 01))
        event.setWholeDay(True)
        d = event_util.date_for_display(event)
        self.assertEqual(d['from_str'], 'Jan 01, 2009')
        self.assertEqual(d['to_str'], None)
        self.assertEqual(d['same_day'], True)

    def testSeveralDaysEvent(self):
        self.login('god')
        self.portal.invokeFactory('VSEvent', id='foo')
        event = self.portal['foo']
        event.setStartDate(DateTime(2009, 01, 01))
        event.setEndDate(DateTime(2009, 12, 31))
        event.setWholeDay(True)
        d = event_util.date_for_display(event)
        self.assertEqual(d['from_str'], 'Jan 01, 2009')
        self.assertEqual(d['to_str'], 'Dec 31, 2009')
        self.assertEqual(d['same_day'], False)

    def testiCalVSEvent(self):
        self.login('god')
        self.portal.invokeFactory('VSEvent', id='foo')
        event = self.portal['foo']
        data = event.getICal()

    def testiCalVSSubEvent(self):
        self.login('god')
        self.portal.invokeFactory('VSSubEvent', id='foo')
        event = self.portal['foo']
        data = event.getICal()

    def testVCal(self):
        self.login('god')
        self.portal.invokeFactory('VSEvent', id='foo')
        event = self.portal['foo']
        data = event.getVCal()

class RecurrenceTest(TestBase):

    def testRecurranceBasic(self):
        self.login('god')
        # Basic recurrence, daily for one year:
        self.folder.invokeFactory('VSEvent', 'event')
        event = getattr(self.folder, 'event')
        event.update(startDate = DateTime('2001/02/01 10:00'),
                     endDate = DateTime('2001/02/01 14:00'))

        # Mark as recurring
        zope.interface.alsoProvides(event, kalends.IRecurringEvent)
        recurrence = kalends.IRecurrence(event)

        # Set the recurrence info
        event.frequency=rrule.DAILY
        event.until=DateTime('2002/02/01')
        event.interval = 1
        event.count = None

        # Test
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 2).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2002, 2, 1).toordinal())
        self.failUnlessEqual(len(dates), 365)

        # Try with an interval
        event.interval = 3
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 4).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2002, 1, 30).toordinal())
        self.failUnlessEqual(len(dates), 121)

        # Have a max count:
        event.count = 25
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(len(dates), 24)

    def testRecurranceMidnight(self):
        # Check that the recurrence works correctly with events starting
        # at midnight
        self.login('god')
        self.folder.invokeFactory('VSEvent', 'event')
        event = getattr(self.folder, 'event')

        event.update(startDate = DateTime('2001/02/01 00:00'),
                     endDate = DateTime('2001/02/01 04:00'))

        # Mark as recurring
        zope.interface.alsoProvides(event, kalends.IRecurringEvent)
        recurrence = kalends.IRecurrence(event)

        # Set the recurrence info
        event.frequency=rrule.DAILY
        event.until=DateTime('2001/02/04')
        event.interval=1
        event.count=None

        # Test
        dates = recurrence.getOccurrenceDays()        
        self.failUnlessEqual(dates[0], datetime.date(2001, 2, 2).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2001, 2, 4).toordinal())
        self.failUnlessEqual(len(dates), 3)

    def testRecurranceWeek(self):
        self.login('god')
        self.folder.invokeFactory('VSEvent', 'event')
        event = getattr(self.folder, 'event')

        event.update(startDate = DateTime('2007/02/01 00:00'),
                     endDate = DateTime('2007/02/01 04:00'))

        # Mark as recurring
        zope.interface.alsoProvides(event, kalends.IRecurringEvent)
        recurrence = kalends.IRecurrence(event)

        # Set the recurrence info
        event.frequency=rrule.WEEKLY
        event.until=DateTime('2008/02/04')
        event.interval=1
        event.count=None

        # Test
        dates = recurrence.getOccurrenceDays()
        self.failUnlessEqual(dates[0], datetime.date(2007, 2, 8).toordinal())
        self.failUnlessEqual(dates[1], datetime.date(2007, 2, 15).toordinal())
        self.failUnlessEqual(dates[2], datetime.date(2007, 2, 22).toordinal())
        self.failUnlessEqual(dates[-1], datetime.date(2008, 1, 31).toordinal())
        self.failUnlessEqual(len(dates), 52)


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTests(makeSuite(VSEventTest))
    suite.addTests(makeSuite(RecurrenceTest))
    suite.layer = layer.ZCMLLayer
    return suite
