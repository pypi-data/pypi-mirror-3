from zope.interface import implements, implementer, Interface
from zope.component import adapter
from zope.annotation import IAnnotations

from zope.schema.interfaces import ITitledTokenizedTerm
from zope.i18n import translate
from zope.app.intid.interfaces import IIntIds
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import IFormLayer, IFieldWidget, DISPLAY_MODE
from z3c.form.widget import FieldWidget
from z3c.relationfield.interfaces import IRelationList
from Products.CMFCore.utils import getToolByName


class IGroupingCheckboxWidget(Interface):
    """Interface for the person grouping listing widget
    """


class GroupingCheckboxWidget(CheckBoxWidget):
    implements(IGroupingCheckboxWidget)
    klass = u'persongrouping-selection-widget'

    @property
    def _portal_types(self):
        return getToolByName(self.context, 'portal_types')

    def update(self):
        super(GroupingCheckboxWidget, self).update()
        self.portal_types = self._portal_types

    @property
    def grouped_items(self):
        """Build a list of items used to render the widget values."""
        items = {}
        for item in self.items:
            term_value = self.terms.getValue(item['value'])
            portal_type = term_value.portal_type
            items.setdefault(portal_type, [])            
            grouping = items[portal_type]
            # XXX We shouldn't be looking this up just yet. Wait for the
            #     user to select the option.
            groupdata_type = term_value.groupdata_type
            # Add some FSD specific data.
            # TODO refactor this into a less FSD specific form.
            additional_item_info = {
                'description': term_value.get('description', None),
                # 'url': ?,
                'groupdata_type': groupdata_type,
                }
            # Update the item directly, which will change the values in self.items
            item.update(additional_item_info)
            grouping.append(item)
            items[portal_type] = sorted(grouping, key=lambda i: i['label'])
        return items

    @property
    def displayValue(self):
        values = {}
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByToken(token)
            type = term.value.portal_type
            type = self._portal_types.getTypeInfo(type).Title()
            values.setdefault(type, [])
            if ITitledTokenizedTerm.providedBy(term):
                title = translate(term.title, context=self.request,
                                  default=term.title)
            else:
                title = term.token
            info = {'title': title,
                    'url': term.value.absolute_url(),
                    }
            values[type].append(info)
            values[type] = sorted(values[type], key=lambda d: d['title'])
        values = sorted(values.items(), key=lambda v: v[0])
        return values


@adapter(IRelationList, IFormLayer)
@implementer(IFieldWidget)
def GroupingCheckboxFieldWidget(field, request):
    return FieldWidget(field, GroupingCheckboxWidget(request))
