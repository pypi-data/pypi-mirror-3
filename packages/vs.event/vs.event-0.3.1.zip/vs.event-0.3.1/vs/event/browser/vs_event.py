################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Walther
################################################################

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from App.class_init import InitializeClass
from vs.event.config import *
from vs.event.content import event_util
import random

class VSView(BrowserView):
    """ """

    def add_supplementary_event(self):
        """ create a new supplementary event"""
        calendar = getToolByName(self.context, 'portal_calendar')
        if not calendar.vs_event_supplementary_events:
            raise RuntimeError('portal_calendar.vs_event_supplementary_events '
                               ' is not enabled')
        id = self.context.getId() + '-' + str(random.random())
        self.context.invokeFactory('VSSubEvent', id=id)
        event = self.context[id]
        event.setTitle(self.context.Title())
        event.setDescription(self.context.Description())
        event.setExcludeFromNav(True)
        sub_events = self.context.getSubEvents() or []
        sub_events.append(event)
        self.context.setSubEvents(sub_events)
        self.request.response.redirect(event.absolute_url() + '/edit')

    def date_for_display(self):
        """ Return dict containing pre-calculated information for 
            building a <start>-<end> date string.
        """
        return event_util.date_for_display(self.context)

InitializeClass(VSView)
