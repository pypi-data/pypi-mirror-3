from plone.theme.interfaces import IDefaultPloneLayer
from plone.portlets.interfaces import IPortletManager

from plonetheme.intkBase.browser.interfaces import IIntkBaseLayer
from zope.interface import implements, Interface

class IThemeSpecific(IIntkBaseLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
    
class ISidebarManager(IPortletManager):
 """Portlets on the permanent sidebar"""


class IHomeManager(IPortletManager):
 """Portlets on the permanent sidebar"""