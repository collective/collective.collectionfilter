# -*- coding: utf-8 -*-
import json

from Acquisition import aq_inner
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import safe_unicode
from collective.collectionfilter.filteritems import get_filter_items
from collective.collectionfilter.query import make_query
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.utils import safe_encode
from collective.collectionfilter.vocabularies import TEXT_IDX
from plone.api.portal import get_registry_record as getrec
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer.interfaces import IIDNormalizer
from six.moves.urllib.parse import urlencode
from zope.component import queryUtility
from zope.i18n import translate

try:
    from collective.geolocationbehavior.interfaces import IGeoJSONProperties
    from plone.formwidget.geolocation.vocabularies import _
    HAS_GEOLOCATION = True
except ImportError:
    HAS_GEOLOCATION = False


class BaseView(object):
    """Abstract base filter view class.
    """
    _collection = None
    _top_request = None

    @property
    def settings(self):
        return self.data

    @property
    def available(self):
        return True

    @property
    def filter_id(self):
        raise NotImplementedError

    @property
    def title(self):
        return getattr(
            self.settings,
            'header',
            getattr(self.collection, 'Title', u'')
        )

    @property
    def filterClassName(self):
        name = self.title and queryUtility(IIDNormalizer).normalize(self.title)
        return u'filter' + name.capitalize() if name else ''

    @property
    def reload_url(self):
        raise NotImplementedError

    @property
    def top_request(self):
        if not self._top_request:
            self._top_request = get_top_request(self.request)
        return self._top_request

    @property
    def collection(self):
        if not self._collection:
            self._collection = uuidToCatalogBrain(
                self.settings.target_collection
            )
        return aq_inner(self._collection)


class BaseFilterView(BaseView):

    @property
    def input_type(self):
        if self.settings.input_type == 'links':
            return 'link'
        elif self.settings.filter_type == 'single':
            if self.settings.input_type == 'checkboxes_radiobuttons':
                return 'radio'
            else:
                return 'dropdown'
        else:
            return 'checkbox'

    def results(self):
        results = get_filter_items(
            target_collection=self.settings.target_collection,
            group_by=self.settings.group_by,
            filter_type=self.settings.filter_type,
            narrow_down=self.settings.narrow_down,
            show_count=self.settings.show_count,
            view_name=self.settings.view_name,
            cache_enabled=self.settings.cache_enabled,
            request_params=self.top_request.form or {}
        )
        return results


class BaseSearchView(BaseView):

    @property
    def value(self):
        return safe_unicode(self.top_request.get(TEXT_IDX, ''))

    @property
    def action_url(self):
        return self.collection.getURL()

    @property
    def urlquery(self):
        urlquery = {}
        urlquery.update(self.top_request.form)
        for it in (
            TEXT_IDX,
            'b_start',
            'b_size',
            'batch',
            'sort_on',
            'limit',
            'portlethash'
        ):
            # Remove problematic url parameters
            if it in urlquery:
                del urlquery[it]
        return urlquery

    @property
    def ajax_url(self):
        # Recursively transform all to unicode
        request_params = safe_decode(self.top_request.form)
        urlquery = base_query(request_params, extra_ignores=['SearchableText'])
        query_param = urlencode(safe_encode(urlquery), doseq=True)
        ajax_url = u'/'.join([it for it in [
            self.collection.getURL(),
            self.settings.view_name,
            '?' + query_param if query_param else None
        ] if it])
        return ajax_url


if HAS_GEOLOCATION:

    class BaseMapsView(BaseView):

        @property
        def ajax_url(self):
            # Recursively transform all to unicode
            request_params = safe_decode(self.top_request.form)
            urlquery = base_query(
                request_params, extra_ignores=['latitude', 'longitude'])
            query_param = urlencode(safe_encode(urlquery), doseq=True)
            ajax_url = u'/'.join([it for it in [
                self.collection.getURL(),
                self.settings.view_name,
                '?' + query_param if query_param else None
            ] if it])
            return ajax_url

        @property
        def locations(self):
            custom_query = {}  # Additional query to filter the collection

            collection = uuidToObject(self.settings.target_collection)
            if not collection:
                return None

            # Recursively transform all to unicode
            request_params = safe_decode(self.top_request.form or {})

            # Get all collection results with additional filter
            # defined by urlquery
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

                feature = {
                    'type': 'Feature',
                    'id': it.UID,
                    'properties': {},
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            it.longitude,
                            it.latitude,
                        ]
                    }
                }

                props = IGeoJSONProperties(it.getObject(), None)
                if getattr(props, 'popup', None):
                    feature['properties']['popup'] = props.popup
                if getattr(props, 'color', None):
                    feature['properties']['color'] = props.color
                if getattr(props, 'extraClasses', None):
                    feature['properties']['extraClasses'] = props.extraClasses

                features.append(feature)

            if not features:
                return

            geo_json = json.dumps({
                'type': 'FeatureCollection',
                'features': features
            })
            return geo_json

        @property
        def map_configuration(self):
            config = {
                "fullscreencontrol": getrec('geolocation.fullscreen_control'),
                "locatecontrol": getrec('geolocation.locate_control'),
                "zoomcontrol": getrec('geolocation.zoom_control'),
                "minimap": getrec('geolocation.show_minimap'),
                "default_map_layer": self.settings.default_map_layer,
                "map_layers": [
                    {"title": translate(_(it), context=self.request), "id": it}
                    for it in self.settings.map_layers
                ],
            }
            return json.dumps(config)
