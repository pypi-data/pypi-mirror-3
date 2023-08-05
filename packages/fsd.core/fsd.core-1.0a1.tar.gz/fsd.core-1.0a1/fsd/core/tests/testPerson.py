from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContent, createContentInContainer
from z3c.relationfield import RelationValue
from zc.relation.interfaces import ICatalog
from zope.annotation import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent

from Products.Archetypes.interfaces import IUIDCatalog
from fsd.core.tests import unittest
from fsd.core import GROUPDATA_REFERENCE_ANNOTATION, GROUPDATA_CONTAINER
from fsd.core.groupdata import IGroupData
from fsd.core.tests.base import PersonTestCaseMixIn, FSD_CORE_INTEGRATION_TESTING


class PersonIntegrationTest(unittest.TestCase):

    layer = FSD_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

    def testCustomNameAdapter(self):
        createContentInContainer(self.portal, 'fsd.core.person',
                                 firstName='bob', lastName='Smith',
                                 checkConstraints=False)
        self.assertTrue('bob-smith' in self.portal.objectIds())

    def testSortableTitleIndex(self):
        createContentInContainer(self.portal, 'fsd.core.person',
                                 firstName='bob', lastName='Smith',
                                 checkConstraints=False)
        self.assertTrue(len(self.catalog({'sortable_title':'smith bob'})), 1)

    def testUIDCatalogIndexing(self):
        createContentInContainer(self.portal, 'fsd.core.person',
                                 firstName='bob', lastName='Smith',
                                 checkConstraints=False)
        notify(ObjectCreatedEvent(self.portal['bob-smith']))

        catalog = getToolByName(self.portal, 'uid_catalog')

        self.fail("Missing assertion...")


class PersonRelationships(unittest.TestCase, PersonTestCaseMixIn):

    layer = FSD_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        # Create People
        createContentInContainer(self.portal, 'fsd.core.person', 
                                 firstName='bob', lastName='Smith',
                                 checkConstraints=False)
        createContentInContainer(self.portal, 'fsd.core.person', 
                                 firstName='Robin', lastName='Blue',
                                 checkConstraints=False)
        # Create Groups
        createContentInContainer(self.portal, 'fsd.core.persongrouping',
                                 title='Chemistry', checkConstraints=False)
        self.intids = getUtility(IIntIds)
        self.relCatalog = getUtility(ICatalog)
        # Register the testing GroupData content type
        from plone.dexterity.fti import ftiAdded, DexterityFTI
        from zope.lifecycleevent import ObjectAddedEvent
        fti = DexterityFTI(u'fsd.core.tests.groupdata')
        fti.schema = u"fsd.core.tests.testGroupData.IAlsoSubclassGroupData"
        ftiAdded(fti, ObjectAddedEvent(fti, self.portal, fti.getId()))

    def testRemovingRelationshipRemovesGroupData(self):
        # Local variable assignments
        person = self.portal['bob-smith']
        group = self.portal['chemistry']
        groupIID = self.intids.getId(group)
        self.addPersonToGroup(person, group)
        # Trigger the subscriber(s) that handle group data modifications
        notify(ObjectModifiedEvent(person))
        self.assertTrue(str(groupIID) in person[GROUPDATA_CONTAINER].objectIds())

        # Delete the groups to verify the removal of group data
        person.groups = []
        notify(ObjectModifiedEvent(person))
        self.assertTrue(str(groupIID) not in person[GROUPDATA_CONTAINER].objectIds())

        # Ensure that removing the related group also deletes the associated groupdata.
        createContentInContainer(self.portal, 'fsd.core.persongrouping',
                                 title='Biology', checkConstraints=False)
        # (new) Local variable assignments
        # person2 has been introduced to verify that the subscriber is run on all known relationships.
        person2 = self.portal['robin-blue']
        group = self.portal['biology']
        groupIID = self.intids.getId(group)
        self.addPersonToGroup(person, group)
        notify(ObjectModifiedEvent(person))
        self.addPersonToGroup(person2, group)
        notify(ObjectModifiedEvent(person2))

        self.assertTrue(str(groupIID) in person[GROUPDATA_CONTAINER].objectIds())
        self.assertEqual(person2[GROUPDATA_CONTAINER].objectIds(), [str(groupIID)])
        # Remove a group and check for group relations on the person.
        del(self.portal['biology'])
        self.assertTrue(str(groupIID) not in person[GROUPDATA_CONTAINER].objectIds())
        self.assertEqual(person2[GROUPDATA_CONTAINER].objectIds(), [])
