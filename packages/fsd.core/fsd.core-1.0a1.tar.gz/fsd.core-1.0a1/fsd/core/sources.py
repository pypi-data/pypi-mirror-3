# -*- coding: utf-8 -*-
from zope.interface import directlyProvides, implements
from zope.interface.interface import Attribute, InterfaceClass, Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from z3c.form.interfaces import ITerms
from z3c.formwidget.query.interfaces import IQuerySource
from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.ParseTree import ParseError
from plone.app.vocabularies.catalog import parse_query


class BrainTerm(object):
    """ZCatalog brain term for use with SimpleVocabulary."""
    implements(ITokenizedTerm)

    def __init__(self, brain):
        # FIXME Grabbing the object is bad, but the IDataManager for
        #       the z3c.form widget did it first! We need to find a solution
        #       that doesn't involve poking every single object.
        self.value = brain.getObject()
        self.brain = brain
        self.token = brain.UID
        self.title = brain.has_key('Title') and brain.Title or None
        if self.title is not None:
            directlyProvides(self, ITitledTokenizedTerm)


class ICatalogQuerySource(IQuerySource, ITerms):
    """Catalog query produces a source of vocabulary terms."""

    criteria = Attribute("Criteria or filter used in the catalog query")

    def getBrainByToken(token):
        """Return the brain object that matches the given token.
        None will be returned if the token couldn't be found."""

    def getTermByBrain(brain):
        """Return a Term from the given ZCatalog brain."""


class ITypedCatalogQuerySource(ICatalogQuerySource):
    """A catalog query source that groups the results into individual
    vocabularies by major type."""

    type = Attribute("The iface of the type to be queried")


# ########### #
#   Sources   #
# ########### #

class CatalogQuerySource(object):
    """See IQuerySource"""
    implements(ICatalogQuerySource)

    def __init__(self, context, criteria):
        self.context = context
        self.criteria = criteria
        brains = self._catalog(**self.criteria)
        terms = [BrainTerm(b) for b in brains]
        self._vocabulary = SimpleVocabulary(terms)

    @property
    def _catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    #
    # ITerms
    #
    def __contains__(self, item):
        # Note: item is the value of a term not the term or token.
        return item in self._vocabulary

    def __len__(self):
        return self._vocabulary.__len__()

    def __iter__(self):
        return self._vocabulary.__iter__()

    def getTerm(self, value):
        return self._vocabulary.getTerm(value)

    def getValue(self, token):
        return self.getTermByToken(token).value

    def getTermByToken(self, token):
        return self._vocabulary.getTermByToken(token)

    #
    # IQuerySource
    #
    def search(self, query_string):
        portal_url = getToolByName(self.context, "portal_url")
        portal_path = portal_url.getPortalPath()
        # Update the given query string with the sources query string, to
        # ensure the scope of our query stays within bounds.
        query = parse_query(query_string, portal_path)
        query.update(self.criteria)

        try:
            results = list([self.getTermByBrain(brain)
                            for brain in self._catalog(**query)])
        except ParseError:
            return []

        return results

    #
    # ICatalogQuerySource
    #
    def getBrainByToken(self, token):
        try:
            term = self._vocabulary.getTermByToken(token)
            # XXX Eek, a term attribute that has not interface association.
            value = term.brain
        except LookupError:
            value = None
        return value

    def getTermByBrain(self, brain):
        # Instantiate a new brain term to get it's token, but don't return it,
        # because it differs from the original in _vocabulary.
        return self.getTermByToken(BrainTerm(brain).token)


class TypedCatalogQuerySource(CatalogQuerySource):
    """See ITypedCatalogQuerySource"""
    implements(ITypedCatalogQuerySource)

    def __init__(self, context, type_, criteria={}):
        if not isinstance(type_, InterfaceClass):
            raise TypeError("Expected an Interface, got a %s" % type(type_))
        self.type = type_
        criteria.update(dict(object_provides=self.type.__identifier__))
        super(TypedCatalogQuerySource, self).__init__(context, criteria)


# ################## #
#   Source Binders   #
# ################## #

class CatalogQuerySourceBinder(object):
    """See IContextSourceBinder"""
    implements(IContextSourceBinder)

    def __init__(self, **criteria):
        self.criteria = criteria

    def __call__(self, context):
        return CatalogQuerySource(context, self.criteria)


class TypedCatalogQuerySourceBinder(object):
    """See IContextSourceBinder"""
    implements(IContextSourceBinder)

    def __init__(self, type_iface, **criteria):
        self.type = type_iface
        self.criteria = criteria

    def __call__(self, context):
        return TypedCatalogQuerySource(context, self.type, self.criteria)
