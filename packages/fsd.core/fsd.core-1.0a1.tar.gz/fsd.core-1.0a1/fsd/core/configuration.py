from zope import schema
from zope.interface import Interface
from fsd.core.persongrouping import groupdataTypes

class IGroupDataMapping(Interface):
    groupdataType = schema.Choice(title=u"Group Data Type",
                                  source=groupdataTypes)
