from zope.component import ComponentLookupError
from plone.indexer.decorator import indexer
import zope.interface

from dateable import kalends

@indexer(kalends.IRecurringEvent)
def recurrence_days(object, **kwargs):
    """Return the dates of recurrences as ordinals
    """
    try:
        recurrence = kalends.IRecurrence(object)
        return recurrence.getOccurrenceDays()
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

