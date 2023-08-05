import logging
from persistent.mapping import PersistentMapping
from OFS.interfaces import IObjectWillBeRemovedEvent

from zope.component import getUtility
from zope.interface import alsoProvides
from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent, IObjectModifiedEvent,)
from five import grok

from zope.annotation import IAnnotations, IAttributeAnnotatable
from zope.app.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog

from zope import schema
from z3c.relationfield.schema import RelationList, RelationChoice

from plone.app.content.interfaces import INameFromTitle
from plone.app.content.namechooser import NormalizingNameChooser
from plone.dexterity.content import Container
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer import indexer

from fsd.core import (
    _, GROUPDATA_CONTAINER,
    GROUPDATA_REFERENCE_ANNOTATION, GROUPDATA_DELETION_ANNOTATION,
    )
from fsd.core.base import IFSDContent
from fsd.core.persongrouping import IPersonGrouping
from fsd.core.sources import TypedCatalogQuerySourceBinder
from fsd.core.widgets import GroupingCheckboxFieldWidget


logger = logging.getLogger('fsd.core')


class IPerson(IFSDContent, form.Schema):
    """A Person with a first name, last name and group relationship."""

    firstName = schema.TextLine(
        title=_(u"First Name"),
        )

    lastName = schema.TextLine(
        title=_(u"Last Name"),
        )

    form.widget(groups=GroupingCheckboxFieldWidget)
    groups = RelationList(
        title=u"Groups",
        description=u"",
        default=[],
        required=False,
        value_type=RelationChoice(
            title=_(u"Groups"),
            source=TypedCatalogQuerySourceBinder(IPersonGrouping),
            )
        )


class Person(Container):

    def Title(self):
        return "%s %s" % (self.firstName, self.lastName)


# =========
# = Views =
# =========

# class View(grok.View):
#     grok.context(IPerson)
#     grok.require('zope2.View')

# ============
# = Adapters =
# ============

class TitleAdapter(grok.Adapter):
    grok.provides(INameFromTitle)
    grok.context(IPerson)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return NormalizingNameChooser(self.context).chooseName(self.context.Title(), self.context)

# ==========
# = Events =
# ==========

def _log_person_to_groupid_relationship(doing, person, gid):
    """Helper function to log a relationship and what is being done."""
    # Check for the log level before doing work.
    if logger.isEnabledFor(logging.DEBUG):
        to_path = lambda o: '/'.join(o.getPhysicalPath())
        intids = getUtility(IIntIds)
        if not isinstance(gid, int):
            gid = int(gid)
        # Determine the object path
        person_path = to_path(person)
        group_path = to_path(intids.getObject(gid))
        logger.debug("%s FSD Person -> Group relationship "
                     "(%s -> %s)" % (doing, person_path, group_path,))


@grok.subscribe(IPerson, IObjectModifiedEvent)
def updateGroupDataContent(obj, event):
    """Add or remove groupdata content objects for person->group relationships."""
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    obj_id = intids.getId(obj)
    groupdata_container = obj[GROUPDATA_CONTAINER]
    rels = list(catalog.findRelations({'from_id': obj_id, 'from_attribute': 'groups'}))

    # Delete any groupdata content remaining from a deleted relationship
    relation_ids = [str(rel.to_id) for rel in rels if not rel.isBroken()]
    groupdata_ids_to_remove = [id for id in groupdata_container.objectIds()
                               if id not in relation_ids]
    for id in groupdata_ids_to_remove:
        _log_person_to_groupid_relationship("Removing GroupData container for", obj, id)
        del(groupdata_container[id])

    # XXX This should be done during relationship creation. There is likely a better
    #     place (event) for this logic.
    for rel in rels:
        # Make sure all group relations are annotatable
        if not IAttributeAnnotatable.providedBy(rel):
            alsoProvides(rel, IAttributeAnnotatable)
            # Assign the groupdata reference to a default value.
            IAnnotations(rel).setdefault(GROUPDATA_REFERENCE_ANNOTATION, None)


@grok.subscribe(IPersonGrouping, IObjectWillBeRemovedEvent)
def deleteUnlinkedGroupDataContent(obj, event):
    """Unlink (remove) the GroupData content from the related people."""
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    gid = intids.getId(obj)
    group_id = str(gid)
    relations_to_group = catalog.findRelations({'to_id': gid,
                                                'from_attribute': 'groups'})

    # Delete any groupdata content remaining from a deleted relationship
    for relation in relations_to_group:
        annotation = IAnnotations(relation)
        # XXX We need a better solution, because this sucks...
        # Set a deletion flag on the relation for the object modification
        #    subscriber to catch. Otherwise, the subscriber will add
        #    a new GroupData object.
        annotation[GROUPDATA_DELETION_ANNOTATION] = True
        person = intids.getObject(relation.from_id)
        groupdata_container = person[GROUPDATA_CONTAINER]
        if group_id in groupdata_container:
            groupdata = groupdata_container[group_id]
            del(groupdata)


@grok.subscribe(IPerson, IObjectAddedEvent)
def createGroupDataStorage(obj, event):
    """Generate a basic folder to store groupdata content within this person."""
    if logger.isEnabledFor(logging.DEBUG):
        path = '/'.join(obj.getPhysicalPath())
        logger.debug("Creating the GroupData container for %s" % path)
    obj[GROUPDATA_CONTAINER] = Container(GROUPDATA_CONTAINER)

# ===========
# = Indexes =
# ===========

@indexer(IPerson)
def SortableTitle(obj):
    return "%s %s" % (obj.lastName.lower(), obj.firstName.lower())
grok.global_adapter(SortableTitle, name="sortable_title")
