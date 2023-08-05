# -*- coding: utf-8 -*-

################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Walther
################################################################

from StringIO import StringIO
from config import PROJECTNAME, DEPENDENCIES
from Products.CMFCore.utils import getToolByName

class Generator(object):

    def installProducts(self, p, out):
        """QuickInstaller install of required Products"""
        qi = getToolByName(p, 'portal_quickinstaller')
        for product in DEPENDENCIES:
            if qi.isProductInstalled(product):
                qi.reinstallProducts([product])
            else:
                qi.installProduct(product, locked=0)
                print >> out, "Product installed: %s \n" %product

    def setCalendarProperties(self, p, out):
        tool = getToolByName(p , 'portal_calendar')
        types = list(tool.getCalendarTypes())
        for id in ('VSEvent', 'VSSubEvent'):
            if not id in types:
                types.append(id)
        tool.calendar_types = tuple(types)
        if not tool.hasProperty('vs_event_supplementary_events'):
            tool.manage_addProperty('vs_event_supplementary_events', True, 'boolean')
        print >> out, "VSEvent types for Calendar activated \n" 


def setupVarious(context):

    if context.readDataFile('vs.event_various.txt') is None:
        return
    # Add additional setup code here
    out = StringIO()
    site = context.getSite()
    gen = Generator()
    gen.installProducts(site, out)
    gen.setCalendarProperties(site, out)
    logger = context.getLogger(PROJECTNAME)
    logger.info(out.getvalue())
