from zope.interface import implements
from zope.component import adapts
from archetypes.schemaextender import field
from archetypes.schemaextender.interfaces import (
    IOrderableSchemaExtender, IBrowserLayerAwareExtender)
from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IBaseObject
from zest.social import ZestSocialMessageFactory as _
from zest.social import config
from zest.social.interfaces import IZestSocialLayer


class ExtensionBooleanField(field.ExtensionField, atapi.BooleanField):
    """An extended BooleanField."""


class SocialBookmarkingSchemaExtender(object):
    """An extender for adding extra information about social bookmarking.
    """

    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    adapts(IBaseObject)
    layer = IZestSocialLayer

    _fields = [
        ExtensionBooleanField(
            'show_social_viewlet',
            schemata='settings',
            widget=atapi.BooleanWidget(
                label=_(
                    u'title_show_social_viewlet',
                    default=u"Show social bookmarking viewlet"),
                description=_(
                    u'description_show_social_viewlet',
                    default=(u"If selected, allows sharing this content on "
                             u"social bookmarking sites, showing links near "
                             u"the bottom of the page.")),
                ),
            default=config.SHOW_VIEWLET_DEFAULT,
            ),
        ]

    def __init__(self, context=None):
        self.context = context

    def getFields(self):
        return self._fields

    def getOrder(self, original):
        return original
