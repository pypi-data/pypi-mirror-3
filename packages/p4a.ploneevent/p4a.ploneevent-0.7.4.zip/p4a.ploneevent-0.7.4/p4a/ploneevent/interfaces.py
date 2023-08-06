from zope import interface

class IEventSchemaExtension(interface.Interface):
    
    def getFields():
        """Returns all the fields as a list"""
        
    def getOrders():
        """Returns a list of tuples of (order, schemataname)"""