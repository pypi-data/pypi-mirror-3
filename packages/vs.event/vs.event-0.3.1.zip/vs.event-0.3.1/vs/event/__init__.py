# -*- coding: utf-8 -*-
################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Walther 
################################################################

from zope.i18nmessageid import MessageFactory
from config import PROJECTNAME

from Products.CMFCore import utils
from Products.Archetypes import atapi

MessageFactory = MessageFactory(PROJECTNAME)
from config import PROJECTNAME
from logging import getLogger
log = getLogger(">>>>>>>>")

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(PROJECTNAME),
        PROJECTNAME)

    ADD_PERMISSIONS={}
    for type in content_types:
        ADD_PERMISSIONS[type.portal_type] = """Add %s""" %type.portal_type

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (PROJECTNAME, atype.portal_type),
        content_types      = (atype,),
        permission         = ADD_PERMISSIONS[atype.portal_type],
        extra_constructors = (constructor,),
        ).initialize(context)


#from Products.CMFCore.permissions import setDefaultRoles
#setDefaultRoles('Add VSEvent', ('Manager', ))
