from zope import schema
from zope.interface import Interface
from plone.app.deco import PloneMessageFactory as _


class IDecoLayer(Interface):
    """Marker interface for the registry adapter"""


class IWeightedDict(Interface):
    name = schema.TextLine(title=_(u"Name"))
    label = schema.TextLine(title=_(u"Label"))
    weight = schema.Int(title=_(u"Weight"))


class IFormat(Interface):
    """Interface for the format configuration in the registry"""
    name = schema.TextLine(title=_(u"Name"))
    category = schema.TextLine(title=_(u"Category"))
    label = schema.TextLine(title=_(u"Label"))
    action = schema.TextLine(title=_(u"Action"))
    icon = schema.Bool(title=_(u"Icon"))
    favorite = schema.Bool(title=_(u"Favorite"))
    weight = schema.Int(title=_(u"Weight"))


class IAction(Interface):
    name = schema.TextLine(title=_(u"Name"))
    fieldset = schema.TextLine(title=_(u"Fieldset"))
    label = schema.TextLine(title=_(u"Label"))
    action = schema.TextLine(title=_(u"Action"))
    icon = schema.Bool(title=_(u"Icon"))
    menu = schema.Bool(title=_(u"Menu"))
    weight = schema.Int(title=_(u"Weight"))


class IFieldTile(Interface):
    """Interface for the field tile configuration in the registry
    """
    id = schema.TextLine(title=_(u"The widget id"))
    name = schema.TextLine(title=_(u"Name"))
    label = schema.TextLine(title=_(u"Label"))
    category = schema.TextLine(title=_(u"Category"))
    tile_type = schema.TextLine(title=_(u"Type"))
    read_only = schema.Bool(title=_(u"Read only"))
    favorite = schema.Bool(title=_(u"Favorite"))
    widget = schema.TextLine(title=_(u"Field widget"))
    available_actions = schema.List(title=_(u"Actions"),
                                    value_type=schema.TextLine())


class ITile(Interface):
    """ Interface for the tile configuration in the registry.
    """

    name = schema.TextLine(
            title=_(u"Name"),
            required=True,
            )
    label = schema.TextLine(
            title=_(u"Label"),
            required=True,
            )
    group = schema.TextLine(
            title=_(u"Group"),
            required=True,
            default=u'default',
            )
    icon = schema.TextLine(
            title=_(u"Label"),
            default=u'++resource++plone.app.deco/default_tile_icon.png',
            )


class IWidgetAction(Interface):
    name = schema.TextLine(title=_(u"Name"))
    actions = schema.List(title=_(u"Actions"),
                          value_type=schema.TextLine())


class IMetadataTile(Interface):
    """Metadata tiles are application tiles that handle metadata
    """

    def get_value(self):
        """Returns the value to display through the template.
        """
