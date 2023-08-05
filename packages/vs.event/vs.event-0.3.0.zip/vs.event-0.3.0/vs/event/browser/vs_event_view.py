################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Walther
################################################################

from plone.memoize.instance import memoize
from datetime import date 
from dateable.kalends import IRecurrence
from dateutil.parser import parse
from zope.i18n import translate
from App.class_init import InitializeClass
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent, View
from dateable.kalends import IRecurringEvent

from vs.event.config import *
from vs.event.interfaces import IVSSubEvent
from vs.event.browser.dtutils import dt2DT
from vs.event import MessageFactory as _

FREQ = {0: _('year'),
        1: _('month'),
        2: _('week'),
        3: _('day'),
        4: _('hour'),
        5: _('minute'),
        6: _('second'),
    }

class VSEventView(BrowserView):
    """ vs_event_view browser view """

    def same_day(self):
        return self.context.start().Date() == self.context.end().Date()

    def short_start_date(self):
        return self.context.toLocalizedTime(self.context.start(), long_format=0)
        
    def long_start_date(self):
        return self.context.toLocalizedTime(self.context.start(), long_format=1)
    
    def start_time(self):
        return self.context.start().strftime(self.time_format())

    def short_end_date(self):
        return self.context.toLocalizedTime(self.context.end(), long_format=0)
    
    def long_end_date(self):
        return self.context.toLocalizedTime(self.context.end(), long_format=1)

    def end_time(self):
        return self.context.end().strftime(self.time_format())

    def datetime_format(self):
        site_properties = self.context.portal_properties.site_properties
        return site_properties.getProperty('localLongTimeFormat')

    def date_format(self):
        site_properties = self.context.portal_properties.site_properties
        return site_properties.getProperty('localTimeFormat')
    
    def time_format(self):
        datetime_format = self.datetime_format()
        if '%p' in datetime_format:
            # Using AM/PM:
            return ' '.join(datetime_format.split(' ')[-2:])
        # 24 H format
        return datetime_format.split(' ')[-1]

    def isRecurring(self):
        return IRecurringEvent.providedBy(self.context)

    def rrule(self):
        return IRecurrence(self.context, None).getRecurrenceRule()

    def rrule_freq(self):
        rrule = self.rrule()
        if rrule is None:
            return ''
            
        # mapping can't be in translate() method (actually, it can, but translation does not work).
        mapping={'interval':rrule._interval, 
                 'frequency':FREQ[rrule._freq]}
        if rrule._interval == 1:
            text = _(u"vs_text_every_freq", u"Every ${frequency}", mapping)
        else:
            text = _(u"vs_text_every_interval_freq", u"Every ${interval}. ${frequency}s", mapping)

        return translate(text)
        
    def rrule_interval(self):
        rrule = self.rrule()
        if rrule is not None:
            return rrule._interval
        return 0
        
    def rrule_end(self):
        rrule = self.rrule()
        if rrule is not None and rrule._until:
            return self.context.toLocalizedTime(dt2DT(rrule._until), long_format=0)
        return ''

    @memoize    
    def filteredAttendees(self):
        """ return list of attendees with 'show' flag set """
        attendees = self.context.getAttendees()
        result = []
        for attendee in attendees:
            if attendee['show']:
                result.append(attendee)
        return result

    def getMainEvent(self):
        """ return the main event from the list of backrefs """

        backrefs = self.context.getBRefs()
        if backrefs:
            return backrefs[0]
        return None

    def getSupplementaryEvents(self):
        """ return list of suppl. events in sorted order """

        sm = getSecurityManager()
        events = self.context.getSubEvents()
        events = [ev for ev in events if sm.checkPermission(View, ev)]
        events.sort(lambda e1,e2: cmp(e1.start(), e2.start()))
        return events

    @memoize
    def nextDates(self):
        """ Recurrence """
        return [ date.fromordinal(x) for x in IRecurrence(self.context, None).getOccurrenceDays()]
 
    @memoize
    def getExceptions(self):
        """ get recurrence exceptions """
        return [parse(x) for x in self.context.getExceptions()]


    @memoize
    def toLocalizedTime(self, time, long_format=None):
        """Convert time to localized time
        """
        properties=getToolByName(self.context, 'portal_properties').site_properties
        if long_format:
            format=properties.localLongTimeFormat
        else:
            format=properties.localTimeFormat

        return time.strftime(format)

    @memoize
    def allowedToAddSubEvents(self):
        """ Security chess """
        return getSecurityManager().checkPermission(ModifyPortalContent, self)


    @memoize
    def subeventsEnabled(self):
        """Convert time to localized time
        """
        calendar = getToolByName(self.context, 'portal_calendar')
        return getattr(calendar, 'vs_event_supplementary_events', False)


    @memoize
    def isSubEvent(self):
        """ check if the current object is a VSSubEvent """
        return IVSSubEvent.providedBy(self.context)


    def getAttachments(self):
        """ Return all viewable attachments """
        if self.isSubEvent():
            return ()
        mtool = self.context.portal_membership
        result = []
        objs = self.context.getAttachments()
        return [o for o in objs if mtool.checkPermission('View', o)]

InitializeClass(VSEventView)
