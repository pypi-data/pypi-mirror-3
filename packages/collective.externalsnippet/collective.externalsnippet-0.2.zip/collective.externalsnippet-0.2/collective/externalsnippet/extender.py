from zope.interface import implements
from zope.component import adapts

from archetypes.schemaextender.interfaces import (ISchemaExtender, IBrowserLayerAwareExtender)
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes.atapi import AnnotationStorage

from Products.Archetypes.atapi import (StringField, StringWidget, PasswordWidget,
                                       BooleanField, BooleanWidget)
from Products.CMFCore.permissions import ModifyPortalContent

from collective.externalsnippet import _
from collective.externalsnippet.interfaces import IExternalSnippetMarker, IExternalSnippetSpecific

class ExStringField(ExtensionField, StringField):
    """ A string field """

class ExBooleanField(ExtensionField, BooleanField):
    """ A boolean field """

class SnippetExtender(object):
    """ Add fields for external snippet settings. """
    adapts(IExternalSnippetMarker)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IExternalSnippetSpecific
    
    fields = [
        ExStringField("snippetURL",
            schemata = 'settings',
            languageIndependent = True,
            default = '',
            write_permission = ModifyPortalContent,
            validators = ('isURL',),
            storage = AnnotationStorage(),
            widget = StringWidget(
                label = _(u"label_snippet_url",
                    default = u"Snippet URL"),
                description = _(u"help_snippet_url",
                    default = u"Enter URL address for page which will be rendered in the default view as external snippet."),
            ),
        ),
        
        ExStringField("snippetExpression",
            schemata = 'settings',
            languageIndependent = True,
            default = '.*<BODY.*?>(.*?)</BODY>',
            write_permission = ModifyPortalContent,
            storage = AnnotationStorage(),
            widget = StringWidget(
                label = _(u"label_snippet_expression",
                    default = u"Snippet Expression"),
                description = _(u"help_snippet_expression",
                    default = u"Enter regular expression which will be used to match external page's content."),
            ),
        ),
        
        ExStringField("snippetUsername",
            schemata = 'settings',
            languageIndependent = True,
            default = '',
            write_permission = ModifyPortalContent,
            storage = AnnotationStorage(),
            widget = StringWidget(
                label = _(u"label_snippet_username",
                    default = u"Snippet Username"),
                description = _(u"help_snippet_username",
                    default = u"Enter username for basic authentication if required."),
            ),
        ),
        
        ExStringField("snippetPassword",
            schemata = 'settings',
            languageIndependent = True,
            default = '',
            write_permission = ModifyPortalContent,
            storage = AnnotationStorage(),
            widget = PasswordWidget(
                label = _(u"label_snippet_password",
                    default = u"Snippet Password"),
                description = _(u"help_snippet_password",
                    default = u"Enter password for basic authentication if required."),
            ),
        ),

        ExBooleanField("snippetSupportCookies",
            schemata = 'settings',
            languageIndependent = True,
            default = False,
            write_permission = ModifyPortalContent,
            storage = AnnotationStorage(),
            widget = BooleanWidget(
                label = _(u"label_support_cookies",
                    default = u"Support cookies"),
                description = _(u"help_support_cookies",
                    default = u"Some external applications with basic authentication requires cookies support."),
            ),
        ),
        
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
