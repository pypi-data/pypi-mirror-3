# Trying to use archetypes.schemaextender
from zope import component, interface
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.Archetypes.utils import OrderedDict
from Products.ATContentTypes.content.event import ATEvent
from dateable.kalends import IRecurringEvent
from p4a.ploneevent.interfaces import IEventSchemaExtension
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
from p4a.ploneevent import PloneEventMessageFactory as _
from Products.Archetypes.utils import IntDisplayList
class TextField(ExtensionField, atapi.TextField):
     pass

class DateTimeField(ExtensionField, atapi.DateTimeField):
     pass

class IntegerField(ExtensionField, atapi.IntegerField):
     pass

class StringField(ExtensionField, atapi.StringField):
     pass

freqDisplayList = IntDisplayList([(-1, _(u'Does not repeat')),
                                  (YEARLY, _(u'Yearly')),
                                  (MONTHLY, _(u'Monthly')),
                                  (WEEKLY, _(u'Weekly')),
                                  (DAILY, _(u'Daily'))])

class RecurrenceExtension(object):
     component.adapts(IOrderableSchemaExtender, IRecurringEvent)
     interface.implements(IEventSchemaExtension)

     fields = [
          IntegerField('frequency',
               schemata='recurrence',
               required=True,
               vocabulary=freqDisplayList,
               default=-1,
               widget=atapi.SelectionWidget(label=_(u'Repeats'))
               ),
          IntegerField('interval',
               schemata='recurrence',
               required=True,
               default=1,
               widget=atapi.IntegerWidget(label=_(u'Repeats every'),
                    description=_(u'Repeats every day/week/month/year.'))
               ),
          DateTimeField('until',
               schemata='recurrence',
               widget=atapi.CalendarWidget(label=_(u'Range'),
                    description=_(u'Event repeats until this date.'),
                    show_hm=True)
               ),
          IntegerField('count',
                schemata='recurrence',
                widget=atapi.IntegerWidget(label=_(u'Count'),
                    description=_(u'Maximum number of times the event repeats'),)
                ),
          ]

     def __init__(self, extender, context):
          pass

     def getFields(self):
          return self.fields
     
     def getOrders(self):
          return [(10, 'recurrence')]
