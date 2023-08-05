from zope.interface import alsoProvides
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer

from z3c.form.interfaces import IFormLayer, IContextAware, DISPLAY_MODE
from plone.uuid.interfaces import IUUID
from plone.z3cform.tests import setup_defaults as setup_z3cform_defaults

from fsd.core.testing import make_type
from fsd.core.tests import unittest
from fsd.core.tests.base import PersonTestCaseMixIn, FSD_CORE_INTEGRATION_TESTING


class GroupingCheckboxWidgetTest(unittest.TestCase, PersonTestCaseMixIn):

    layer = FSD_CORE_INTEGRATION_TESTING

    def setUp(self):
        # Plone itegration bits
        setup_z3cform_defaults()
        # Local variables set up by the layer
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # Apply the form layer interface to the request for adapatation
        # within the widget.
        alsoProvides(self.request, IFormLayer)
        # Create a contextual objects.
        self.context = createContentInContainer(self.portal, 'fsd.core.person',
                                                firstName='bob', lastName='smith',
                                                checkConstraints=False)
        self.group = createContentInContainer(self.portal, 'fsd.core.persongrouping',
                                              title='Groupies',
                                              text="blah",
                                              # XXX Bad type name, not resolvable!
                                              groupdata_type='fsd.core.tests.groupdata',
                                              checkConstraints=False)
        self.addPersonToGroup(self.context, self.group, create_groupdata=False)

    def _makeOne(self, context):
        # Make the widget and assign the context
        from fsd.core.person import IPerson
        field = IPerson['groups']
        from fsd.core.widgets import GroupingCheckboxFieldWidget
        widget = GroupingCheckboxFieldWidget(field, self.request)
        # Bypass the __call__ my manually setting context
        # and making the widget context aware
        widget.context = context
        alsoProvides(widget, IContextAware)
        return widget

    def test_grouping_by_type(self):
        from fsd.core.persongrouping import IPersonGrouping
        groupie_fti = make_type('IGroupie', schema=IPersonGrouping)
        club_fti = make_type('IClub', schema=IPersonGrouping)
        group = createContentInContainer(self.portal, groupie_fti.getId(),
                                         id='poison', title="Poison",
                                         checkConstraints=False)
        club = createContentInContainer(self.portal, club_fti.getId(),
                                        id='spee', title="Spee Final Club",
                                        checkConstraints=False)

        widget = self._makeOne(self.context)
        widget.update()

        grouped_by_type = widget.grouped_items
        self.assertIn(groupie_fti.getId(), grouped_by_type)
        self.assertIn(club_fti.getId(), grouped_by_type)
        club_uuid = IUUID(club)
        item = [i for i in widget.items if i['value'] == club_uuid][0]
        self.assertEqual(grouped_by_type[club_fti.getId()][0], item)

    def test_items(self):
        widget = self._makeOne(self.context)
        widget.update()

        # Check that all three groups made it into the items list.
        self.assertEqual(len(widget.items), 1)
        self.assertEqual(self.group.title, widget.items[0]['label'])
        self.assertTrue(widget.items[0]['checked'])


@unittest.skip("No tests implemented yet")
class PersonGroupingIntegrationTest(unittest.TestCase):

    layer = FSD_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

    def test_nothing(self):
        pass
