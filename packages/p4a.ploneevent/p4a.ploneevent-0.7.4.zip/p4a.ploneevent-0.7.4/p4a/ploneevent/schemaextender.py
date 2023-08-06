# XXX I'm wondering if this could be moved to a separate product, or
# p4a.subtyper or integrated into Archetypes SchemaExtender or something, as
# it is quite generic except for the IRecurrence interface.

from zope import component, interface
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.Archetypes.utils import OrderedDict
from Products.ATContentTypes.content.event import ATEvent

from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
from interfaces import IEventSchemaExtension

class TextField(ExtensionField, atapi.TextField):
     pass

class DateTimeField(ExtensionField, atapi.DateTimeField):
     pass

class IntegerField(ExtensionField, atapi.IntegerField):
     pass

class StringField(ExtensionField, atapi.StringField):
     pass

class EventSchemaExtender(object):
     component.adapts(ATEvent)
     interface.implements(IOrderableSchemaExtender)

     def __init__(self, context):
          self.context = context

     def getFields(self):          
          fields = []
          for name, extension in component.getAdapters((self, self.context),
                                                       IEventSchemaExtension):
               fields.extend(extension.getFields())
          return fields
     
     def getOrder(self, original):
          res = OrderedDict()
          
          # Make "default" come first:          
          res['default'] = original['default']
          del original['default']
          
          # Go through any extensions:
          schematas = []
          for name, extension in component.getAdapters((self, self.context),
                                                       IEventSchemaExtension):
               schematas.extend(extension.getOrders())
          schematas.sort()
          for order, schemata in schematas:
               res[schemata] = original[schemata]
               del original[schemata]
          
          # And tag on anything left over:
          res.update(original)
          self._order = res
          return res
