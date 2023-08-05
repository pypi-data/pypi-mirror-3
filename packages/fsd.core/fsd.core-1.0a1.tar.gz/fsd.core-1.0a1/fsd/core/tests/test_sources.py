# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces._content import IContentish
from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID
from plone.dexterity.interfaces import IDexterityContainer, IDexterityItem
from plone.dexterity.utils import createContentInContainer

from fsd.core.testing import make_type
from fsd.core.tests import unittest
from fsd.core.tests.base import FSD_CORE_INTEGRATION_TESTING


class CatalogQuerySourceTestCase(unittest.TestCase):

    layer = FSD_CORE_INTEGRATION_TESTING

    def setUp(self):
        # Local variables
        self.portal = self.layer['portal']
        self.content_fti = make_type('IContent', schema=IDexterityItem)
        self.container_fti = make_type('IContainer', schema=IDexterityContainer)
        # Create fake content
        createContentInContainer(self.portal, str(self.content_fti.getId()),
                                 id='one', title="One", checkConstraints=False)
        createContentInContainer(self.portal, str(self.content_fti.getId()),
                                 id='two', title="Two", checkConstraints=False)
        createContentInContainer(self.portal, str(self.container_fti.getId()),
                                 id='folder', title="Folder",
                                 checkConstraints=False)

    def test_results(self):
        iface_ident = str(self.content_fti.schema)
        query_criteria = dict(object_provides=iface_ident)
        # Make a source
        from fsd.core.sources import CatalogQuerySourceBinder
        binder = CatalogQuerySourceBinder(**query_criteria) 
        source = binder(self.portal)
        # Query the catalog for the expected results
        catalog = getToolByName(self.portal, 'portal_catalog')
        results = catalog(**query_criteria)
        # Check the length of the source matches the length query results. (__len__)
        self.assertEqual(len(source), len(results))
        # Verify one of the results is 'in' the source. (__contains__)
        key = results[0].UID
        self.assertIn(key, [x.token for x in source])
        # Verify the iteration is working correctly. (__iter__)
        # And that the get_brain_from_token works as expected.
        for term in source:
            # The term value is a brain but we want to verify the method works.
            rid = source.getBrainByToken(term.token).getRID()
            self.assertIn(rid, [b.getRID() for b in results])

    def test_search_augments(self):
        iface_ident = str(self.content_fti.schema)
        query_criteria = dict(object_provides=iface_ident)
        # Make a source
        from fsd.core.sources import CatalogQuerySource
        source = CatalogQuerySource(self.portal, query_criteria.copy())
        # Query the catalog for the expected results
        catalog = getToolByName(self.portal, 'portal_catalog')

        # Update the query to be more specific
        text = 'One'
        query_string = text
        query_criteria['SearchableText'] = text
        results = catalog(**query_criteria)
        source_results = source.search(query_string)
        # Check the length of the source matches the length query results. (__len__)
        self.assertEqual(len(source_results), len(results))
        # Verify the results are equal.
        self.assertEqual(source.getBrainByToken(source_results[0].token).getRID(),
                         results[0].getRID())

        # Try again with an term that shouldn't be in the source.
        # This tests that the search stays within the predefined scope.
        query_string = 'Folder'
        source_results = source.search(query_string)
        # Check the length of the source matches the length query results. (__len__)
        self.assertEqual(len(source_results), 0)


class TypedCatalogQuerySourceTestCase(unittest.TestCase):

    layer = FSD_CORE_INTEGRATION_TESTING

    def setUp(self):
        # Local variables
        self.portal = self.layer['portal']
        # Create a master type to base other types on.
        self.master_fti = make_type('ICanCount', schema=IDexterityItem)
        self.master_schema = self.master_fti.lookupSchema()
        # Create subtypes from master
        self.subtype_one_fti = make_type('ISubtypeOne', schema=self.master_schema)
        self.subtype_two_fti = make_type('ISubtypeTwo', schema=self.master_schema)
        # Create content
        createContentInContainer(self.portal, str(self.master_fti.getId()),
                                 id='zero', title="Zero",
                                 checkConstraints=False)
        createContentInContainer(self.portal, str(self.subtype_one_fti.getId()),
                                 id='one', title="One",
                                 checkConstraints=False)
        createContentInContainer(self.portal, str(self.subtype_two_fti.getId()),
                                 id='two', title="Two",
                                 checkConstraints=False)
        createContentInContainer(self.portal, str(self.subtype_two_fti.getId()),
                                 id='three', title="Three",
                                 checkConstraints=False)

    def test_results(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        group_by_type = self.master_fti.lookupSchema()
        # Make the source
        from fsd.core.sources import TypedCatalogQuerySourceBinder
        binder = TypedCatalogQuerySourceBinder(group_by_type)
        source = binder(self.portal)

        # Check the length of the source matches the number of grouped types. (__len__)
        self.assertEqual(len(source), 4)
        # Verify one of the results is 'in' the source. (__contains__)
        brain = catalog(id='three')[0]
        term = source.getTermByBrain(brain)
        self.assertIn(term.value, source)
        # Verify the iteration is working correctly. (__iter__)
        # And that the get_brain_from_token works as expected.
        term = source.getTermByToken(brain.UID)
        # Compare by RID since brain comparison doesn't apear to work here.
        self.assertEqual(source.getBrainByToken(brain.UID).getRID(),
                         brain.getRID())

    def test_search_augments(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        group_by_type = self.master_fti.lookupSchema()

        # Make a source
        from fsd.core.sources import TypedCatalogQuerySource
        source = TypedCatalogQuerySource(self.portal, group_by_type)

        # Update the query to be more specific
        content_one = self.portal['one']
        content_two = self.portal['two']
        source_results = source.search(content_one.title)
        # Check the length of the source matches the length query results. (__len__)
        self.assertIn(source.getTermByToken(IUUID(content_one)), source_results)
        self.assertNotIn(IUUID(content_two), [term.token for term in source_results])

        # Verify the results are equal.
        term = source.getTermByToken(IUUID(content_one))
        brain = catalog(id=content_one.id)[0]
        # Note: The brains will not directly equal one another. (__eq__)
        self.assertEqual(term.value, brain.getObject())

        # Try again with a term that shouldn't be in the source.
        # This tests that the search stays within the predefined scope.
        fti = make_type('ICobra')
        content = createContentInContainer(self.portal, str(fti.schema),
                                           id='commander', title="Cobra Commander",
                                           checkConstraints=False)
        query_string = 'Cobra'
        source_results = source.search(query_string)
        # Check the length of the source matches the length query results.
        self.assertEqual(len(source_results), 0)
