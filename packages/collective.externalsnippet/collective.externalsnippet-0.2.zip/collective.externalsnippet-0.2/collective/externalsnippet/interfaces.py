from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IExternalSnippetSpecific(IDefaultPloneLayer):
    """ A marker interface that defines a Zope 3 browser layer. """

class IExternalSnippetMarker(Interface):
    """ A content which can have external snippet assigned. """
