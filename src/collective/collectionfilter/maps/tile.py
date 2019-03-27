# -*- coding: utf-8 -*-
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.utils import get_top_request
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseFilterView
from collective.collectionfilter.maps.interfaces import ICollectionMapsSchema
from collective.collectionfilter.query import make_query
from collective.collectionfilter.tiles import DictDataWrapper
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.geolocationbehavior.geolocation import IGeolocatable
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.uuid.utils import uuidToObject
from plone.supermodel.model import Schema
from plone.tiles.tile import PersistentTile
from plone.uuid.interfaces import IUUID
from zope.interface import implementer

import json
import plone.api


class IMapsTile(Schema, ICollectionMapsSchema):
    pass


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
        catalog_results = ICollection(collection).results(
            batch=False,
            brains=True,
            custom_query=custom_query
        )
        if not catalog_results:
            return None
        return catalog_results

    def popup_text(self, event, location):
        popup_text = u"""
<header><a href="{0}">{1}</a></header>
<p>{2}</p>
            """.format(
                event.absolute_url(),
                event.title,
                location.title,
            )
        return popup_text

    @property
    def data_geojson(self):
        """Return the geo location as GeoJSON string.
        """
        features = []

        for it in self.locations:
            ob = it.getObject()
            location_uid = getattr(ob, 'location_uid', None)
            location = uuidToObject(location_uid) if location_uid else None
            geo = IGeolocatable(location, None) if location else None
            if not geo:
                continue

            features.append({
                'type': 'Feature',
                'id': IUUID(ob),
                'properties': {'popup': self.popup_text(ob, location)},
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        geo.geolocation.longitude,
                        geo.geolocation.latitude,
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
        map_layers = plone.api.portal.get_registry_record(
            'collective.venue.map_layers') or []
        config = {
            "default_map_layer": plone.api.portal.get_registry_record(
                'collective.venue.default_map_layer'),
            "map_layers": [
                {"title": _(it), "id": it}
                for it in map_layers
            ],
        }
        return json.dumps(config)
