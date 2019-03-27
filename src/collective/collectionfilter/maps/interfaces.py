# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.interfaces import ICollectionFilterBaseSchema
from zope import schema

default_map_layer = 'OpenStreetMap.Mapnik'

default_map_layers = [
    'OpenStreetMap.Mapnik',
    'Esri.WorldImagery',
    'CartoDB.DarkMatter',
]


class ICollectionMapsSchema(ICollectionFilterBaseSchema):
    """Schema for the search filter.
    """

    default_map_layer = schema.Choice(
        title=_(
            u'default_map_layer',
            u'Default map layer'
        ),
        description=_(
            u'help_default_map_layer',
            default=u'Set the default map layer'
        ),
        required=False,
        default=default_map_layer,
        vocabulary='collective.collectionfilter.map_layers'
    )

    map_layers = schema.List(
        title=_(u'label_map_layers', u'Map Layers'),
        description=_(
            u'help_map_layers',
            default=u'Set the available map layers'),
        required=False,
        default=default_map_layers,
        missing_value=[],
        value_type=schema.Choice(vocabulary='collective.collectionfilter.map_layers'))  # noqa: E501
