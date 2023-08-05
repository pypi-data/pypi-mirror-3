from dateable import kalends
from zope.component import ComponentLookupError
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

def recurrence_days(object, portal, **kwargs):
    """Return the dates of recurrences as ordinals
    """
    try:
        recurrence = kalends.IRecurrence(object)
        return recurrence.getOccurrenceDays()
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('recurrence_days', recurrence_days)
