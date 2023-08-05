# -*- coding: utf-8 -*-
# $Id: recurrence.py 265 2009-06-10 07:47:58Z ajung $

import datetime
from dateutil import rrule
from zope import interface
from zope import component
from zope import schema
from zope.annotation import interfaces as annointerfaces
from dateable import kalends
from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from dtutils import DT2dt

from vs.event.content.event import VSEvent


wdays = [MO, TU, WE, TH, FR, SA, SU]

class IRecurrenceConfig(interface.Interface):
    """Configuration information for an event.
    """
    
    is_recurring = schema.Bool(
        title=u'Recurring event',
        description=u'This event recurs'
        )

class VSRecurrenceSupport(object):
    """Recurrence support"""
    
    interface.implements(kalends.IRecurrence)
    component.adapts(VSEvent)
    
    def __init__(self, context):
        self.context = context

    def getRecurrenceRule(self):
        """Returns a dateutil.rrule"""
        if getattr(self.context, 'frequency', -1) is -1:
            return None
        
        dtstart = DT2dt(self.context.startDate)
        if self.context.until is not None:
            until = DT2dt(self.context.until)
            until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            until = None
        # Make it end at the end of the day:
        indizies = [int(i) for i in self.context.getWeekdays()]
        days = []
        bysetpos = None
        for i in indizies:
            days.append(wdays[i])
        
        if self.context.getBysetpos():
            bysetpos = [int(i) for i in self.context.getBysetpos().split(',')] 
                
        rule = rrule.rrule(self.context.frequency,
                       dtstart=dtstart,
                       interval=self.context.interval,
                       #wkst=None, 
                       count=self.context.count, 
                       until=until, 
                       # byweekday=days,
                       # bysetpos=self.context.getBysetpos(),
                       #bysetpos=None,
                       #bymonth=None, bymonthday=None, byyearday=None, byeaster=None,
                       #byweekno=None, byweekday=None,
                       #byhour=None, byminute=None, bysecond=None,
                       #cache=False
                   )
        if days and bysetpos:
            rule = rrule.rrule(self.context.frequency,
                           dtstart=dtstart,
                           interval=self.context.interval,
                           #wkst=None, 
                           count=self.context.count, 
                           until=until, 
                           byweekday=days,
                           bysetpos=bysetpos,
                           #bysetpos=None,
                           #bymonth=None, bymonthday=None, byyearday=None, byeaster=None,
                           #byweekno=None, byweekday=None,
                           #byhour=None, byminute=None, bysecond=None,
                           #cache=False
                       )
        
        
        return rule

    def getOccurrenceDays(self, until=None):
        """Days on which the event occurs. Used for indexing"""
        # XXX Handle when there is no occurrence.
        rule = self.getRecurrenceRule()
        if rule is None:
            return []
        if until is None:
            until = datetime.datetime.now() + \
                    datetime.timedelta(365*5)

        if until.tzinfo is None and rule._dtstart.tzinfo is not None:
            until = until.replace(tzinfo=rule._dtstart.tzinfo)
            
        if until.tzinfo is not None and rule._dtstart.tzinfo is None:
            until = until.replace(tzinfo=None)
                            
        if rule._until is None or rule._until > until:
            rule._until = until
        
        to_exclude = self.context.getExceptions()
        return [x.date().toordinal() for x in rule if x.date().strftime('%Y-%m-%d') not in to_exclude ][1:]


class EventRecurrenceConfig(object):
    """An IRecurrenceConfig adapter for events.
    """
    
    interface.implements(IRecurrenceConfig)
    component.adapts(VSEvent)

    def __init__(self, context):
        self.context = context

    def __get_is_recurring(self):
        return kalends.IRecurringEvent.providedBy(self.context) and \
               annointerfaces.IAttributeAnnotatable.providedBy(self.context)
    def __set_is_recurring(self, activated):
        ifaces = interface.directlyProvidedBy(self.context)
        if activated:
            if not kalends.IRecurringEvent.providedBy(self.context):
                ifaces += kalends.IRecurringEvent
            if not annointerfaces.IAttributeAnnotatable.providedBy(self.context):
                ifaces += annointerfaces.IAttributeAnnotatable
            if getattr(self.context, 'layout', None) is not None:
                self.context.layout = 'month.html'
        else:
            if kalends.IRecurringEvent in ifaces:
                ifaces -= kalends.IRecurringEvent
            if getattr(self.context, 'layout', None) is not None:
                delattr(self.context, 'layout')
        interface.directlyProvides(self.context, ifaces)

    is_recurring = property(__get_is_recurring,
                            __set_is_recurring)
