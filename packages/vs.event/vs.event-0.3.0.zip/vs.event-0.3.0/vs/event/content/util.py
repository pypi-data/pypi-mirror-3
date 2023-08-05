# -*- coding: iso-8859-15 -*-

from copy import deepcopy

""" Some helper methods for schema manipulation """

def invisibleFields(schema, *fields):
    """ makes a list of fields invisible """
    for name in fields:
        schema[name].widget.visible = False


def removeFields(schema, *fields):
    """ remove fields from a schema """
    for name in fields:
        del schema[name]


def removeActions(actions, *action_ids):
    """ Create a copy of the action datastructure to avoid overwriting
        of existing action definitions and mark some actions as invisible.
    """

    actions = deepcopy(actions)
    for action in actions:
        if action['id'] in action_ids:
            action['visible'] = 0
    return actions


def changeActionURL(actions, action_id, url):
    """changed the URL for an action without redefining it """
    for action in actions:
        if action['id'] == action_id:
            action['action'] = url


def restrictTypes(folder, types):
    """ set type restrictions to the folder object """

    folder.setConstrainTypesMode(1)
    folder.setImmediatelyAddableTypes(types)
    folder.setLocallyAllowedTypes(types)


def safeCreate(folder, id, portal_type):
    """ return folder[id], create it it does not exisit """
    if not id in folder.objectIds():
        folder.invokeFactory(portal_type, id)
    return getattr(folder, id)
