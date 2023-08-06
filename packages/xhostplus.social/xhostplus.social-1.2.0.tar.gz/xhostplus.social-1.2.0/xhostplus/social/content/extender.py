from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes.public import BooleanWidget
from Products.ATContentTypes.interface.interfaces import IATContentType
from Products.Archetypes.public import BooleanField

from xhostplus.social import socialMessageFactory as _
from xhostplus.social.interfaces import IProductLayer

class SocialBooleanField(ExtensionField, BooleanField):
    """Toggle button for enabling social buttons."""

class BaseExtender(object):
    adapts(IATContentType)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IProductLayer

    fields = [
        SocialBooleanField("socialButtons",
            languageIndependent=1,
            default=True,
            schemata='settings',
            widget = BooleanWidget(
                description=_(u'help_social_buttons', default=u'If selected, this item will show social buttons on the bottom of the content.'),
                label = _(u'label_social_buttons', default=u'Social buttons'),
                visible={'view' : 'hidden',
                         'edit' : 'visible'},
            ),
            required=False,
            searchable=False,
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

