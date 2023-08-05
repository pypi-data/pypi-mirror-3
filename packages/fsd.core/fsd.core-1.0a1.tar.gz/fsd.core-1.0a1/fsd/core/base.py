from zope.interface import Interface
from five import grok
from zope.app.container.interfaces import IObjectAddedEvent
from zope.component import queryUtility
from plone.dexterity.interfaces import IDexterityContent

class IFSDContent(IDexterityContent):
    """Marker for all FSD content types"""

# ============
# = Adapters =
# ============



# ==========
# = Events =
# ==========


