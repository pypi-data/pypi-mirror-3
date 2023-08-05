from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import IFormLayer, IFieldWidget, DISPLAY_MODE
from z3c.form.widget import FieldWidget
from z3c.relationfield.interfaces import IRelationList
from zc.relation.interfaces import ICatalog
from zope import schema
from zope.annotation import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import adapter, queryUtility
from zope.interface import implements, implementer, Interface

from fsd.core import _, GROUPDATA_REFERENCE_ANNOTATION
from fsd.core.base import IFSDContent
from fsd.core.groupdata import groupdataTypes


class IPersonGrouping(IFSDContent, form.Schema):
    """Group of People"""

    text = RichText(
        title=_(u"Body Text"),
        )

    groupdata_type = schema.Choice(
        title=_(u"Group Data Type"),
        source=groupdataTypes,
        )

# =========
# = Views =
# =========

class View(grok.View):
    grok.context(IPersonGrouping)
    grok.require('zope2.View')


class People(grok.View):
    grok.context(IPersonGrouping)
    grok.require('zope2.View')

    def update(self):
        catalog = queryUtility(ICatalog)
        intids = queryUtility(IIntIds)
        group = intids.getId(self.context)
        rels = catalog.findRelations({'to_id': group,
                                      'from_attribute': 'groups'})
        people = []
        for relation in rels:
            person = intids.getObject(relation.from_id)
            groupdata = IAnnotations(relation).get(GROUPDATA_REFERENCE_ANNOTATION, None)
            if groupdata is not None:
                groupdata = groupdata.__of__(self.context)
            people.append((person, groupdata,))
        self.people = people
