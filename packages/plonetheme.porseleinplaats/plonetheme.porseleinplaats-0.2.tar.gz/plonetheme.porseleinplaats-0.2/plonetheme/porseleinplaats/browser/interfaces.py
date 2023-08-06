from plone.theme.interfaces import IDefaultPloneLayer

from plonetheme.intkBase.browser.interfaces import IIntkBaseLayer
from zope.interface import implements, Interface

class IThemeSpecific(IIntkBaseLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
