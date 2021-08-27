# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.collectionfilter import PLONE_VERSION
from collective.collectionfilter.filteritems import (
    get_filter_items,
    get_section_filter_items,
    ICollectionish
)
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.query import make_query
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.utils import safe_encode
from collective.collectionfilter.utils import safe_iterable
from collective.collectionfilter.vocabularies import TEXT_IDX
from plone import api
from plone.api.portal import get_registry_record as getrec
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import instance
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import safe_unicode
from six.moves.urllib.parse import urlencode
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory

import json


try:
    from collective.geolocationbehavior.interfaces import IGeoJSONProperties
    from plone.formwidget.geolocation.vocabularies import _

    HAS_GEOLOCATION = True
except ImportError:
    HAS_GEOLOCATION = False


class BaseView(object):
    """Abstract base filter view class."""

    _collection = None
    _top_request = None

    @property
    def settings(self):
        return self.data

    @property
    def available(self):
        return True

    @property
    def is_available(self):
        return True

    @property
    def filter_id(self):
        raise NotImplementedError

    @property
    def title(self):
        return getattr(self.settings, "header", getattr(self.collection, "Title", u""))

    @property
    def filterClassName(self):
        name = self.title and queryUtility(IIDNormalizer).normalize(self.title)
        return u"filter" + name.capitalize() if name else ""

    @property
    def reload_url(self):
        raise NotImplementedError

    @property
    def top_request(self):
        if not self._top_request:
            self._top_request = get_top_request(self.request)
        return self._top_request

    @property
    def collection_uuid(self):
        if self.settings.target_collection:
            return self.settings.target_collection
        return IUUID(self.context)

    @property
    def collection(self):
        if not self._collection:
            self._collection = uuidToCatalogBrain(self.collection_uuid)
        return aq_inner(self._collection)

    @property
    def pat_options(self):

        return json.dumps(
            {
                "collectionUUID": self.collection_uuid,
                "reloadURL": self.reload_url,
                "ajaxLoad": self.ajax_load,
                "contentSelector": self.content_selector,
            }
        )

    @property
    def content_selector(self):
        if self.settings.content_selector:
            return self.settings.content_selector

        collectionish = ICollectionish(self.collection.getObject()) if self.collection else None
        selector = collectionish.content_selector
        if collectionish is None or not selector:
            return u"#content-core"
        else:
            return selector

    @property
    def ajax_load(self):
        if PLONE_VERSION < "5.1":
            # Due to bug in AJAX load pattern makes it hard to make it work in 5.0.x
            return False

        values = api.portal.get_registry_record("plone.patternoptions")
        if "collectionfilter" in values:
            filterOptions = json.loads(values["collectionfilter"])
            if "ajaxLoad" in filterOptions:
                return filterOptions["ajaxLoad"]
        return True


class BaseFilterView(BaseView):
    @property
    def input_type(self):
        if self.settings.input_type == "links":
            return "link"
        elif self.settings.filter_type == "single":
            if self.settings.input_type == "checkboxes_radiobuttons":
                return "radio"
            else:
                return "dropdown"
        else:
            return "checkbox"

    # results is called twice inside the template in view/available and view/results.  But its expensive so we cache it
    # but just the the lifetime of the view
    @instance.memoize
    def results(self):
        results = get_filter_items(
            target_collection=self.collection_uuid,
            group_by=self.settings.group_by,
            filter_type=self.settings.filter_type,
            narrow_down=self.settings.narrow_down,
            show_count=self.settings.show_count,
            view_name=self.settings.view_name,
            cache_enabled=self.settings.cache_enabled,
            request_params=self.top_request.form or {},
            content_selector=self.settings.content_selector,
        )
        return results

    @property
    def is_available(self):
        if not self.settings.hide_if_empty:
            return True

        if self.settings.narrow_down:
            groupby_criteria = getUtility(IGroupByCriteria).groupby
            idx = groupby_criteria[self.settings.group_by]["index"]
            request_params = safe_decode(self.top_request.form)
            current_idx_value = safe_iterable(request_params.get(idx))
            if current_idx_value:
                return True

        results = self.results()
        return not (results is None or len(results) <= 2)  # 2 becayse we include "All"


class BaseSectionView(BaseView):
    @property
    def input_type(self):
        if self.settings.input_type == "links":
            return "link"
        elif self.settings.filter_type == "single":
            if self.settings.input_type == "checkboxes_radiobuttons":
                return "radio"
            else:
                return "dropdown"
        else:
            return "checkbox"

    @property
    def is_available(self):
        return True

    def results(self):
        results = get_section_filter_items(
            target_collection=self.collection_uuid,
            view_name=self.settings.view_name,
            cache_enabled=self.settings.cache_enabled,
            request_params=self.top_request.form or {},
        )
        return results


class BaseSearchView(BaseView):
    @property
    def value(self):
        return safe_unicode(self.top_request.get(TEXT_IDX, ""))

    @property
    def action_url(self):
        return self.collection.getURL()

    @property
    def urlquery(self):
        urlquery = {}
        urlquery.update(self.top_request.form)

        for it in (
            TEXT_IDX,
            "b_start",
            "b_size",
            "batch",
            "sort_on",
            "limit",
            "portlethash",
        ):
            # Remove problematic url parameters
            if it in urlquery:
                del urlquery[it]

        # add filter trigger if not already there
        if "collectionfilter" not in urlquery:
            urlquery["collectionfilter"] = "1"

        return ((k, vv) for k, v in urlquery.items() for vv in safe_iterable(v))

    @property
    def ajax_url(self):
        # Recursively transform all to unicode
        request_params = safe_decode(self.top_request.form)
        urlquery = base_query(request_params, extra_ignores=["SearchableText"])
        query_param = urlencode(safe_encode(urlquery), doseq=True)
        ajax_url = u"/".join(
            [
                it
                for it in [
                    self.collection.getURL(),
                    self.settings.view_name,
                    "?" + query_param if query_param else None,
                ]
                if it
            ]
        )
        return ajax_url


class BaseSortOnView(BaseView):
    def results(self):
        collection = ICollectionish(self.collection.getObject()).selectContent(self.settings.content_selector)
        if collection is None:
            return
        curr_val = self.top_request.get("sort_on", collection.sort_on)
        curr_order = self.top_request.get(
            "sort_order", "descending" if collection.sort_reversed else "ascending"
        )
        new_order = "ascending"
        if curr_order is not None and curr_order == "ascending":
            new_order = "descending"
        sortable_indexes = getUtility(
            IVocabularyFactory, name="collective.collectionfilter.SortOnIndexes"
        )
        vocab = sortable_indexes(self.context)
        for idx in self.settings.sort_on:
            curr = curr_val == idx
            yield {
                "value": idx,
                "title": vocab.getTerm(idx).title,
                "new_order": new_order if curr else "ascending",
                "curr_order": curr_order if curr else "",
                "active": curr,
            }

    @property
    def ajax_url(self):
        # Recursively transform all to unicode
        request_params = safe_decode(self.top_request.form)
        urlquery = base_query(request_params, extra_ignores=["sort_on", "sort_order"])
        query_param = urlencode(safe_encode(urlquery), doseq=True)
        ajax_url = u"/".join(
            [
                it
                for it in [
                    self.collection.getURL(),
                    self.settings.view_name,
                    "?" + query_param if query_param else None,
                ]
                if it
            ]
        )
        return ajax_url


if HAS_GEOLOCATION:

    class BaseMapsView(BaseView):
        @property
        def ajax_url(self):
            # Recursively transform all to unicode
            request_params = safe_decode(self.top_request.form)
            urlquery = base_query(
                request_params, extra_ignores=["latitude", "longitude"]
            )
            query_param = urlencode(safe_encode(urlquery), doseq=True)
            ajax_url = u"/".join(
                [
                    it
                    for it in [
                        self.collection.getURL(),
                        self.settings.view_name,
                        "?" + query_param if query_param else None,
                    ]
                    if it
                ]
            )
            return ajax_url

        @property
        def locations(self):
            custom_query = {}  # Additional query to filter the collection

            collection = uuidToObject(self.collection_uuid)
            if not collection:
                return None

            # Recursively transform all to unicode
            request_params = safe_decode(self.top_request.form or {})

            # Get all collection results with additional filter
            # defined by urlquery
            custom_query = base_query(request_params)
            custom_query = make_query(custom_query)
            return ICollectionish(collection).selectContent(self.settings.content_selector).results(
                custom_query, request_params)

        @property
        def data_geojson(self):
            """Return the geo location as GeoJSON string."""
            features = []

            for it in self.locations:
                if not it.longitude or not it.latitude:
                    # these ``it`` are brains, so anything which got lat/lng
                    # indexed can be used.
                    continue

                feature = {
                    "type": "Feature",
                    "id": it.UID,
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            it.longitude,
                            it.latitude,
                        ],
                    },
                }

                props = IGeoJSONProperties(it.getObject(), None)
                if getattr(props, "popup", None):
                    feature["properties"]["popup"] = props.popup
                if getattr(props, "color", None):
                    feature["properties"]["color"] = props.color
                if getattr(props, "extraClasses", None):
                    feature["properties"]["extraClasses"] = props.extraClasses

                features.append(feature)

            if not features:
                return

            geo_json = json.dumps({"type": "FeatureCollection", "features": features})
            return geo_json

        @property
        def map_configuration(self):
            config = {
                "fullscreencontrol": getrec("geolocation.fullscreen_control"),
                "locatecontrol": getrec("geolocation.locate_control"),
                "zoomcontrol": getrec("geolocation.zoom_control"),
                "minimap": getrec("geolocation.show_minimap"),
                "default_map_layer": self.settings.default_map_layer,
                "map_layers": [
                    {"title": translate(_(it), context=self.request), "id": it}
                    for it in self.settings.map_layers
                ],
            }
            return json.dumps(config)
