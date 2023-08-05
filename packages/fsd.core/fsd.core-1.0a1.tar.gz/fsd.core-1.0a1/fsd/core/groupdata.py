from five import grok
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import form
from zope import schema
from zope.component import getUtilitiesFor
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from fsd.core import _
from fsd.core.base import IFSDContent


class IGroupData(IFSDContent, form.Schema):
    """Contains Person specific group data.
    For example, Bill (person) is the Head (data)
    of the Accounting (group) department."""

    # I need some sort of data to check against. Once TTW editing is fixed, 
    # this can be removed.
    sampleField = schema.TextLine(
            title=_(u"Sample Field"),
        )

# =========
# = Views =
# =========

class Inline(grok.View):
    grok.context(IGroupData)
    grok.require('zope2.View')


# ================
# = Vocabularies =
# ================
@grok.provider(IContextSourceBinder)
def groupdataTypes(context):
    items = []
    for name, fti in getUtilitiesFor(IDexterityFTI):
        if fti.lookupSchema().isOrExtends(IGroupData):
            items.append(name)
    items.sort(key=lambda x: x.lower())
    return SimpleVocabulary.fromValues(items)