# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.collectionfilter import PLONE_VERSION
from collective.collectionfilter.filteritems import (
    get_filter_items,
    get_section_filter_items,
    ICollectionish,
    _build_url,
    _build_option,
)
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.query import make_query
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.utils import safe_encode
from collective.collectionfilter.utils import safe_iterable
from collective.collectionfilter.vocabularies import TEXT_IDX
from collective.collectionfilter.vocabularies import DEFAULT_TEMPLATES
from collective.collectionfilter.vocabularies import get_conditions
from collective.collectionfilter.vocabularies import EMPTY_MARKER
from plone.api.portal import get_registry_record as getrec
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.utils import iterSchemata
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import instance
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import safe_unicode
from six.moves.urllib.parse import urlencode, parse_qsl
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n import translate
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.Expression import Expression, getExprContext
from plone import api
from plone.memoize import ram
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

        collectionish = (
            ICollectionish(self.collection.getObject()) if self.collection else None
        )
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
            include_all_option=self.settings.enable_all_filter_option,
        )
        if not getattr(self.request, "collectionfilter", None):
            existing_query_string = self.request["QUERY_STRING"]
            # Using `parse_qsl` then converting to a list as `parse_qs` ends up producing lists for the values
            query_object = dict(parse_qsl(existing_query_string))

            if self.settings.group_by not in query_object:
                query_object[self.settings.group_by] = results[0]["value"]

            query_object['collectionfilter'] = 1

            self.request.response.redirect(
                "%s?%s"
                % (self.request["ACTUAL_URL"], urlencode(query_object))
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
        collection = ICollectionish(self.collection.getObject()).selectContent(
            self.settings.content_selector
        )
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


def _exp_cachekey(method, self, target_collection, request):
    return (
        target_collection,
        json.dumps(request),
        self.settings.view_name,
        self.settings.as_links,
    )


def _field_title_cache_key(method, self, field_id):
    return (
        field_id[0],
        self.context.getTypeInfo().id
    )


class BaseInfoView(BaseView):

    # TODO: should just cache on request?
    @ram.cache(_exp_cachekey)
    def get_expression_context(self, collection, request_params):
        count_query = {}
        query = base_query(request_params)
        collection_url = collection.absolute_url()
        # TODO: take out the search
        # TODO: match them to indexes and get proper names
        # TODO: format values properly
        # TODO: do we want to read out sort too?
        count_query.update(query)
        # TODO: delay evaluating this unless its needed
        # TODO: This could be cached as same result total appears in other filter counts
        catalog_results_fullcount = ICollectionish(collection).results(
            make_query(count_query), request_params
        )
        results = len(catalog_results_fullcount)

        # Clean up filters and values
        if "collectionfilter" in query:
            del query["collectionfilter"]
        groupby_criteria = getUtility(IGroupByCriteria).groupby
        q = []
        for group_by, value in query.items():
            if group_by not in groupby_criteria:
                continue
            # TODO: we actually have idx not group_by
            idx = groupby_criteria[group_by]['index']
            value = safe_decode(value)
            current_idx_value = safe_iterable(value)
            # Set title from filter value with modifications,
            # e.g. uuid to title
            display_modifier = groupby_criteria[group_by].get("display_modifier", None)
            titles = []
            for filter_value in current_idx_value:
                title = filter_value
                if filter_value is not EMPTY_MARKER and callable(display_modifier):
                    title = safe_decode(display_modifier(filter_value, idx))
                # TODO: still no nice title for filter indexes? Should be able to get from query builder
                # TODO: we don't know if filter is AND/OR to display that detail
                # TODO: do we want no follow always?
                # TODO: should support clearing filter? e.g. if single value, click to remove?
                # Build filter url query
                query_param = urlencode(
                    safe_encode({group_by: filter_value}), doseq=True
                )
                url = "/".join(
                    [
                        it
                        for it in [
                            collection_url,
                            self.settings.view_name,
                            "?" + query_param if query_param else None,
                        ]
                        if it
                    ]
                )
                # TODO: should have option for nofollow?
                if self.settings.as_links:
                    titles.append(u'<a href="{}">{}</a>'.format(url, title))
                else:
                    titles.append(title)
            q.append((group_by, titles))

        # Set up context for running templates
        expression_context = getExprContext(
            collection,
        )
        expression_context.setLocal("results", results)
        expression_context.setLocal("query", q)
        expression_context.setLocal("search", query.get("SearchableText", ""))
        return expression_context

    def info_contents(self):
        request_params = self.top_request.form or {}
        expression_context = self.get_expression_context(
            self.collection.getObject(), request_params
        )

        parts = []
        for template in self.settings.template_type:
            _, exp = DEFAULT_TEMPLATES.get(template)
            # TODO: precompile templates
            text = Expression(exp)(expression_context)
            if text:
                parts.append(text)
        line = u" ".join(parts)
        # TODO: should be more generic i18n way to do this?
        line = line.replace(u" ,", u",").replace(" :", ":")
        return line

    def is_content_context(self):
        if not self.settings.context_aware:
            return False

        if self.collection.getObject() == self.context:
            return False

        return True

    def get_fields_to_display(self):
        fields = self.settings.context_aware_fields
        # TODO: Get the friendly name for the group_by instead of the id
        return [
            (field, getattr(self.context, field))
            for field in fields
            if hasattr(self.context, field)
        ]

    # Cache this function based on the index id and the dexterity type
    @ram.cache(_field_title_cache_key)
    def get_field_title(self, field):
        """
            Field is a tuple, where the first index is the name of the field and the second the values for that field
            Returns the friendly version of the title when possible, falling
              back to the ID if a firiendly name can't be found.
        """
        index_id = field[0]

        for schema in iterSchemata(context=self.context):
            for field_id, field_object in getFieldsInOrder(schema=schema):
                if field_id == index_id:
                    return field_object.title

        return index_id

    def get_field_values(self, field):
        content_value = field[1]
        index = field[0]
        groupby_criteria = getUtility(IGroupByCriteria).groupby
        request_params = self.top_request.form
        request_params = safe_decode(request_params)
        extra_ignores = [index, index + "_op"]
        urlquery = base_query(request_params, extra_ignores)
        collection = self.collection.getObject()

        # TODO: Refactor the following copied lines from collective.collectionfitler.filteritems into a function
        field_value = content_value() if callable(content_value) else content_value
        # decode it to unicode
        field_value = safe_decode(field_value)
        # Make sure it's iterable, as it's the case for e.g. the subject index.
        field_values = safe_iterable(field_value)
        # allow excluding or extending the field_valueue per index
        groupby_modifier = groupby_criteria[index].get("groupby_modifier", None)

        if not groupby_modifier:
            groupby_modifier = lambda values, cur, narrow: values  # noqa: E731

        field_values = groupby_modifier(field_values, field_value, False)

        field_data = []
        for value in field_values:
            url = _build_url(collection_url=collection.absolute_url(), urlquery=urlquery, filter_value=value, current_idx_value=[], idx=index, filter_type="single")
            data = _build_option(filter_value=value, url=url, current_idx_value=[value], groupby_options=groupby_criteria[index])
            field_data.append(data)

        return field_data

    @property
    def is_available(self):
        target_collection = self.collection
        if target_collection is None:
            return False
        request_params = self.top_request.form or {}
        expression_context = self.get_expression_context(
            target_collection.getObject(), request_params
        )

        conditions = dict((k, (t, e)) for k, t, e in get_conditions())
        if not self.settings.hide_when:
            return True
        for cond in self.settings.hide_when:
            _, exp = conditions.get(cond)
            # TODO: precompile templates
            res = Expression(exp)(expression_context)
            if not res:
                return True
        return False


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
            return (
                ICollectionish(collection)
                .selectContent(self.settings.content_selector)
                .results(custom_query, request_params)
            )

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
