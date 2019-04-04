# -*- coding: utf-8 -*-
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.utils import get_top_request
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseFilterView
from collective.collectionfilter.interfaces import ICollectionFilterBaseSchema
from collective.collectionfilter.query import make_query
from collective.collectionfilter.tiles import DictDataWrapper
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.geolocationbehavior.interfaces import IGeoJSONProperties
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.uuid.utils import uuidToObject
from plone.app.uuid.utils import uuidToURL
from plone.formwidget.geolocation.vocabularies import default_map_layer
from plone.formwidget.geolocation.vocabularies import default_map_layers
from plone.supermodel.model import Schema
from plone.tiles.tile import PersistentTile
from zope import schema
from zope.interface import implementer

import json
import plone.api


class IMapsTile(Schema, ICollectionFilterBaseSchema):
    narrow_down = schema.Bool(
        title=_(u'label_narrow_down_results', default=u'Narrow down result'),
        description=_(
            u'help_narrow_down_results',
            default=u'Narrow down the result after zooming/moving the map.'),
        default=False,
        required=False
    )

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
        vocabulary='plone.formwidget.geolocation.vocabularies.map_layers'
    )

    map_layers = schema.List(
        title=_(u'label_map_layers', u'Map Layers'),
        description=_(
            u'help_map_layers',
            default=u'Set the available map layers'),
        required=False,
        default=default_map_layers,
        missing_value=[],
        value_type=schema.Choice(vocabulary='plone.formwidget.geolocation.vocabularies.map_layers'))  # noqa: E501


@implementer(IMapsTile)
class MapsTile(PersistentTile, BaseFilterView):

    def __init__(self, context, request):
        super(MapsTile, self).__init__(context, request)
        # TODO: does not work, because CMFPlone.resources.browser.resource is
        #       called before this one; subrequest problem
        top_request = get_top_request(request)
        add_bundle_on_request(top_request, 'bundle-leaflet')

    @property
    def edit_url(self):
        if not plone.api.user.has_permission(
            'cmf.ModifyPortalContent',
            obj=self.context
        ):
            return None
        return self.url.replace('@@', '@@edit-tile/')

    @property
    def settings(self):
        return DictDataWrapper(self.data)

    @property
    def filter_id(self):
        return self.id

    @property
    def reload_url(self):
        return self.url

    def collection_url(self):
        return uuidToURL(self.settings.target_collection)

    @property
    def locations(self):
        custom_query = {}  # Additional query to filter the collection

        collection = uuidToObject(self.settings.target_collection)
        if not collection:
            return None

        # Recursively transform all to unicode
        request_params = safe_decode(self.top_request.form or {})

        # Get all collection results with additional filter defined by urlquery
        custom_query = base_query(request_params)
        custom_query = make_query(custom_query)
        return ICollection(collection).results(
            batch=False,
            brains=True,
            custom_query=custom_query
        )

    @property
    def data_geojson(self):
        """Return the geo location as GeoJSON string.
        """
        features = []

        for it in self.locations:
            if not it.longitude or not it.latitude:
                # these ``it`` are brains, so anything which got lat/lng
                # indexed can be used.
                continue

            props = IGeoJSONProperties(it.getObject())

            features.append({
                'type': 'Feature',
                'id': it.UID,
                'properties': {
                    'popup': props.popup,
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        it.longitude,
                        it.latitude,
                    ]
                }
            })

        geo_json = json.dumps({
            'type': 'FeatureCollection',
            'features': features
        })
        return geo_json

    @property
    def map_configuration(self):
        config = {
            "default_map_layer": self.settings.default_map_layer,
            "map_layers": [
                {"title": _(it), "id": it}
                for it in self.settings.map_layers
            ],
        }
        return json.dumps(config)
