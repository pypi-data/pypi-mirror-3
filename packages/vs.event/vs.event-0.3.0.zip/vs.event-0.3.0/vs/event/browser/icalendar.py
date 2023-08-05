################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Walther 
################################################################

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from App.class_init import InitializeClass

class iCalendarView(BrowserView):
    """ ICal export"""

    def icalendar_export(self, events=[], **kw):
        """ iCal export for multiple events """

        if not events:
            catalog = getToolByName(self.context, 'portal_catalog')
            calendar = getToolByName(self.context, 'portal_calendar')

            query = kw.copy()
            query['path'] = '/'.join(self.context.getPhysicalPath())
            cal_types = list(calendar.getCalendarTypes())
            query.update(dict(portal_type=cal_types))

            brains = catalog(query)
            events = [b.getObject() for b in brains]

        try:
            relcalid = self.context.UID()
        except AttributeError:
            relcalid = self.context.portal_url.getPortalObject().getId()

        result = list()
        write = result.append
        write('BEGIN:VCALENDAR')
        write('VERSION:2.0')
        write('X-WR-CALNAME:%s' % self.context.Title().upper())
        write('PRODID:-//Plone 3-vs.event\, Inc//(C) ZOPYX Ltd & Co. KG//EN')
        write('X-WR-RELCALID:%s' % relcalid)
        write('X-WR-TIMEZONE:Europe/Berlin')
        write('CALSCALE:GREGORIAN')
        write('METHOD:PUBLISH')

        for event in events:
            for line in event.getICal().split('\n'):
                write(line)

        write('END:VCALENDAR')

        body = '\n'.join(result)
        setHeader = self.context.request.response.setHeader
        setHeader('Content-Length', len(body))
        setHeader('Content-Type', 'text/x-vcalendar')
        setHeader('Content-Disposition', 'attachment; filename=plone-cal.ics')
        return self.context.request.response.write(body)

    def icalendar_export_event(self):
        """ iCal export for a single event (including subevents) """

        events = [self.context]
        try:
            events.extend(self.context.getSubEvents())
        except (KeyError, AttributeError):
            pass

        return self.icalendar_export(events=events)

InitializeClass(iCalendarView)
