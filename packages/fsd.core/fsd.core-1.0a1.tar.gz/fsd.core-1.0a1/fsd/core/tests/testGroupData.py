from plone.dexterity.fti import DexterityFTI, ftiAdded
from zope import schema
from zope.app.container.contained import ObjectAddedEvent

from fsd.core import _
from fsd.core.tests import unittest
from fsd.core.groupdata import groupdataTypes, IGroupData
from fsd.core.tests.base import FSD_CORE_INTEGRATION_TESTING


class ISubclassGroupData(IGroupData):
    anotherField = schema.TextLine(
        title=_(u"Another Field"),
        )

class IAlsoSubclassGroupData(IGroupData):
    yetAnotherField = schema.TextLine(
        title=_(u"Yet Another Field"),
        required=True,
        )
    

class GroupDataIntegrationTest(unittest.TestCase):
    
    layer = FSD_CORE_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']

    def testGroupdataTypesVocabulary(self):
        types = groupdataTypes(self.portal)
        self.assertEqual([a.token for a in types], ['fsd.core.groupdata'])
        
        # Register our two subtypes
        fti = DexterityFTI(u"Subclass")
        fti.schema = u"fsd.core.tests.testGroupData.ISubclassGroupData"
        ftiAdded(fti, ObjectAddedEvent(fti, self.portal, fti.getId()))

        fti = DexterityFTI(u"Another Subclass")
        fti.schema = u"fsd.core.tests.testGroupData.IAlsoSubclassGroupData"
        ftiAdded(fti, ObjectAddedEvent(fti, self.portal, fti.getId()))

        types = groupdataTypes(self.portal)
        # New subtypes should be there, and in alphabetical order.
        self.assertEqual([a.token for a in types], ['Another Subclass', 'fsd.core.groupdata', 'Subclass'])

