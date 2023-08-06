from dateutil import rrule
from zope import interface
from Products.Five.testbrowser import Browser
from DateTime import DateTime
from Testing import ZopeTestCase
import datetime

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.Five import zcml

import p4a.common
import p4a.ploneevent
from dateable import kalends

PloneTestCase.setupPloneSite(products=("p4a.ploneevent",))

class RecurrenceTest(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        ZopeTestCase.utils.setupCoreSessions(self.app)
        self.addProduct('CMFonFive')
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', p4a.ploneevent)
        zcml.load_config('configure.zcml', p4a.subtyper)

    def testRecurranceBasic(self):
        # Basic recurrence, daily for one year:
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')
        event.update(startDate = DateTime('2001/02/01 10:00'),
                     endDate = DateTime('2001/02/01 14:00'))

        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
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
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')

        event.update(startDate = DateTime('2001/02/01 00:00'),
                     endDate = DateTime('2001/02/01 04:00'))

        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
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
        self.folder.invokeFactory('Event', 'event')
        event = getattr(self.folder, 'event')

        event.update(startDate = DateTime('2007/02/01 00:00'),
                     endDate = DateTime('2007/02/01 04:00'))

        # Mark as recurring
        interface.alsoProvides(event, kalends.IRecurringEvent)
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


    def test_recurrence(self):
        browser = Browser()
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (portal_owner, default_password))
        folder_url = self.folder.absolute_url()

        # Add event
        browser.open(folder_url + '/createObject?type_name=Event')
        form = browser.getForm('event-base-edit')
        form.getControl(name='title').value = 'An Event'
        form.getControl(name='startDate_year').value = ['2007']
        form.getControl(name='startDate_month').value = ['04']
        form.getControl(name='startDate_day').value = ['01']
        form.getControl(name='startDate_hour').value = ['11']
        form.getControl(name='startDate_minute').value = ['00']
        form.getControl(name='endDate_year').value = ['2007']
        form.getControl(name='endDate_month').value = ['04']
        form.getControl(name='endDate_day').value = ['01']
        form.getControl(name='endDate_hour').value = ['11']
        form.getControl(name='endDate_minute').value = ['00']
        # Edit the recurrence info:
        form.getControl(name='frequency').value = ['1']
        form.getControl(name='interval').value = '6'
        form.getControl(name='form.button.save').click()

        # Make sure it's properly indexed:
        cat = self.portal.portal_catalog
        self.failUnless(len(cat(portal_type='Event', recurrence_days=732950)) == 1)

def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTests(makeSuite(RecurrenceTest))
    suite.layer = layer.ZCMLLayer

    return suite
