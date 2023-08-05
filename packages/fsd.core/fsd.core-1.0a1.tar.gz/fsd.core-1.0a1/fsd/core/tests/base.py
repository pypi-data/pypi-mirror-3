from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from plone.dexterity.utils import createContentInContainer
from z3c.relationfield import RelationValue

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.layers import IntegrationTesting
from plone.app.testing.layers import FunctionalTesting

from zope.configuration import xmlconfig


class FSDCorePolicy(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import fsd.core
        xmlconfig.file('meta.zcml', fsd.core, context=configurationContext)
        xmlconfig.file('configure.zcml', fsd.core, context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        quickInstallProduct(portal, 'fsd.core')


FSD_CORE_FIXTURE = FSDCorePolicy()

FSD_CORE_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(FSD_CORE_FIXTURE,),
                       name="FSDCore:Integration")


class PersonTestCaseMixIn(object):

    def addPersonToGroup(self, person, group, create_groupdata=True,
                         groupdata_type=u'fsd.core.groupdata'):
        """Appends the group to the person's list of groups."""
        group_iid = getUtility(IIntIds).getId(group)
        groups = person.groups[:]  # Copy the read-only value.
        groups.append(RelationValue(group_iid))
        person.groups = groups
        if create_groupdata:
            id = str(group_iid)
            from fsd.core import GROUPDATA_CONTAINER
            container = person[GROUPDATA_CONTAINER]
            createContentInContainer(container, groupdata_type,
                                     id=id, checkConstraints=False)
