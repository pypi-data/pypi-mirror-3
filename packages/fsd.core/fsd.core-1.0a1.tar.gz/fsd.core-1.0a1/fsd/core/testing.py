"""Testing functions that help in the testing of the FSD package family
and in some cases the Dexterity content framework.
"""
import os
from zope.interface.interface import InterfaceClass
from zope.dottedname.resolve import resolve
from zope.component.hooks import getSite
from zope.lifecycleevent import ObjectAddedEvent
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.fti import ftiAdded, DexterityFTI


def find_type_prefix(package=__package__, file=__file__):
    """Find the type name prefix from the package and file."""
    module = os.path.basename(file)
    module = module[:module.find('.py')]
    return '.'.join((package, module))

def clone_type(name, module=None, schema=IDexterityContent):
    """Dynamically clone a IDexterityContent type for usage in dumb
    situations."""
    if not schema.isOrExtends(IDexterityContent):
        raise TypeError("%s must extend %s" % (schema, IDexterityContent))

    if module is None:
        # If no module was supplied, we'll put the type here.
        # TODO It might be worth creating a new module, so we don't plow over
        #      anything by accident.
        dotted_name = find_type_prefix()
        module = resolve(dotted_name)

    iface = InterfaceClass(name, bases=(schema,),
                           __module__=module.__name__)
    setattr(module, name, iface)
    # Attach the newly created interface (schema) to a module for
    # dotted name lookup.
    iface = getattr(module, name)
    type_name = unicode(iface.__identifier__)
    return (type_name, iface,)

def register_type(name, schema,
                  behaviors=('plone.app.referenceablebehavior.referenceable.IReferenceable',),
                  add_permission=None):
    """Register a new grouping_type given a name and a schema interface."""
    fti = DexterityFTI(name)
    fti.schema = u'.'.join([schema.__module__, schema.__name__])
    fti.behaviors = behaviors
    if add_permission is not None:
        fti.add_permission = add_permission

    site = getSite()
    # Register with the TypesTool, so that we can get type info
    portal_types = getToolByName(site, 'portal_types')
    portal_types._setObject(str(fti.getId()), fti)

    ftiAdded(fti, ObjectAddedEvent(fti, site, fti.getId()))
    return fti

def make_type(name, schema=IDexterityContent):
    """Make a content type from a name and optionally a base schema."""
    name, schema = clone_type(name, schema=schema)
    return register_type(name, schema)
