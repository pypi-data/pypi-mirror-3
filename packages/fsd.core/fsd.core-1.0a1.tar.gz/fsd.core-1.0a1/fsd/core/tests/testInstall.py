from fsd.core.tests import unittest
from fsd.core.tests.base import FSD_CORE_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName


class InstallationIntegrationTest(unittest.TestCase):

    layer = FSD_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.types = self.portal.portal_types
        self.factory = self.portal.portal_factory
        self.skins = self.portal.portal_skins
        self.pc = getToolByName(self.portal, 'portal_catalog')
        self.workflow = self.portal.portal_workflow

        # self.metaTypes = {'fsd.core.person':    'Person',
        #                   }

    def test_dependencies_installed(self):
        quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(quickinstaller.isProductInstalled('plone.app.dexterity'))


# def test_types_installed(self):
#     for type in self.metaTypes.keys():
#         self.assertTrue(type in self.types.objectIds(), "Content type not installed: %s" % type)
#
# def test_type_titles(self):
#     for type in self.metaTypes.keys():
#         self.assertEquals(self.types[type].Title(), self.metaTypes[type])
