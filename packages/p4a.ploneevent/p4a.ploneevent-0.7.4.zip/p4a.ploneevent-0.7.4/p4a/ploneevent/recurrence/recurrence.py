import datetime
from dateutil import rrule, tz
from zope import interface
from zope import component

try:
    from zope.annotation import interfaces as annointerfaces
except ImportError:
    from zope.app.annotation import interfaces as annointerfaces

from persistent.dict import PersistentDict

from p4a.ploneevent.recurrence import interfaces
from p4a.common.descriptors import anno
from p4a.common.dtutils import DT2dt

from Products.ATContentTypes.content.event import ATEvent

from dateable import kalends

class RecurrenceSupport(object):
    """Recurrence support"""

    interface.implements(kalends.IRecurrence)
    component.adapts(ATEvent)

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

        rule = rrule.rrule(self.context.frequency,
                           dtstart=dtstart,
                           interval=self.context.interval,
                           #wkst=None, 
                           count=self.context.count, 
                           until=until, 
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
        
        return [x.date().toordinal() for x in rule][1:]


class EventRecurrenceConfig(object):
    """An IRecurrenceConfig adapter for events.
    """
    
    interface.implements(interfaces.IRecurrenceConfig)
    component.adapts(ATEvent)

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
