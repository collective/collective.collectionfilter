# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.query import make_query
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.utils import safe_encode
from collective.collectionfilter.utils import safe_iterable
from collective.collectionfilter.vocabularies import DEFAULT_FILTER_TYPE
from collective.collectionfilter.vocabularies import EMPTY_MARKER
from Missing import Missing
from plone.app.contenttypes.behaviors.collection import ICollection
try:
    from plone.app.blocks.layoutbehavior import ILayoutAware
    from plone.app.blocks.layoutbehavior import ILayoutBehaviorAdaptable
except ImportError:
    ILayoutAware = None
from plone.app.event.base import _prepare_range
from plone.app.event.base import guess_date_from
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import start_end_query
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer import idnormalizer
from plone.memoize import ram
from plone.memoize.volatile import DontCache
from six.moves.urllib.parse import urlencode
from zope.component import adapter
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from zope.globalrequest import getRequest
from zope.i18n import translate

import plone.api
import six
import re


try:
    from plone.app.event.browser.event_listing import EventListing
except ImportError:

    class EventListing(object):
        pass


def _results_cachekey(
    method,
    target_collection,
    group_by,
    filter_type=DEFAULT_FILTER_TYPE,
    narrow_down=False,
    show_count=False,
    view_name="",
    cache_enabled=True,
    request_params=None,
):
    if not cache_enabled:
        raise DontCache
    cachekey = (
        target_collection,
        group_by,
        filter_type,
        narrow_down,
        show_count,
        view_name,
        request_params,
        " ".join(plone.api.user.get_roles()),
        plone.api.portal.get_current_language(),
        str(plone.api.portal.get_tool("portal_catalog").getCounter()),
    )
    return cachekey


@ram.cache(_results_cachekey)
def get_filter_items(
    target_collection,
    group_by,
    filter_type=DEFAULT_FILTER_TYPE,
    narrow_down=False,
    show_count=False,
    view_name="",
    cache_enabled=True,
    request_params=None,
):
    request_params = request_params or {}
    custom_query = {}  # Additional query to filter the collection

    collection = uuidToObject(target_collection)
    if not collection or not group_by:
        return None
    collection_url = collection.absolute_url()
    collection = ICollectionish(collection)

    # Recursively transform all to unicode
    request_params = safe_decode(request_params)
    # Things break if sort_order is not a str
    if six.PY2 and "sort_order" in request_params:
        request_params["sort_order"] = str(request_params["sort_order"])

    # Get index in question and the current filter value of this index, if set.
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    idx = groupby_criteria[group_by]["index"]
    current_idx_value = safe_iterable(request_params.get(idx))

    extra_ignores = []
    if not narrow_down:
        # Additive filtering is about adding other filter values of the same
        # index.
        extra_ignores = [idx, idx + "_op"]
    urlquery = base_query(request_params, extra_ignores)

    # Get all collection results with additional filter defined by urlquery
    custom_query.update(urlquery)
    custom_query = make_query(custom_query)

    catalog_results = collection.results(custom_query, request_params)
    if narrow_down and show_count:
        # we need the extra_ignores to get a true count
        # even when narrow_down filters the display of indexed values
        # count_query allows us to do that true count
        count_query = {}
        count_urlquery = base_query(request_params, [idx, idx + "_op"])
        count_query.update(count_urlquery)
        catalog_results_fullcount = collection.results(count_query, request_params)
    if not catalog_results:
        return None

    # Attribute name for getting filter value from brain
    metadata_attr = groupby_criteria[group_by]["metadata"]
    # Optional modifier to set title from filter value
    display_modifier = groupby_criteria[group_by].get("display_modifier", None)
    # CSS modifier to set class on filter item
    css_modifier = groupby_criteria[group_by].get("css_modifier", None)
    # Value blacklist
    value_blacklist = groupby_criteria[group_by].get("value_blacklist", None)
    # Allow value_blacklist to be callables for runtime-evaluation
    value_blacklist = (
        value_blacklist() if callable(value_blacklist) else value_blacklist
    )  # noqa
    # fallback to title sorted values
    sort_key_function = groupby_criteria[group_by].get(
        "sort_key_function", lambda it: it["title"].lower()
    )

    grouped_results = {}
    for brain in catalog_results:

        # Get filter value
        val = getattr(brain, metadata_attr, None)
        if callable(val):
            val = val()
        # decode it to unicode
        val = safe_decode(val)
        # Make sure it's iterable, as it's the case for e.g. the subject index.
        val = safe_iterable(val)

        for filter_value in val:
            if filter_value is None or isinstance(filter_value, Missing):
                continue
            if value_blacklist and filter_value in value_blacklist:
                # Do not include blacklisted
                continue
            if filter_value in grouped_results:
                # Add counter, if filter value is already present
                grouped_results[filter_value]["count"] += 1
                continue

            # Set title from filter value with modifications,
            # e.g. uuid to title
            title = filter_value
            if filter_value is not EMPTY_MARKER and callable(display_modifier):
                title = safe_decode(display_modifier(filter_value, idx))

            # Build filter url query
            _urlquery = urlquery.copy()
            # Allow deselection
            if filter_value in current_idx_value:
                _urlquery[idx] = [it for it in current_idx_value if it != filter_value]
            elif filter_type != "single":
                # additive filter behavior
                _urlquery[idx] = current_idx_value + [filter_value]
                _urlquery[idx + "_op"] = filter_type  # additive operator
            else:
                _urlquery[idx] = filter_value

            query_param = urlencode(safe_encode(_urlquery), doseq=True)
            url = "/".join(
                [
                    it
                    for it in [
                        collection_url,
                        view_name,
                        "?" + query_param if query_param else None,
                    ]
                    if it
                ]
            )

            # Set selected state
            selected = filter_value in current_idx_value
            css_class = "filterItem {0}{1} {2}".format(
                "filter-" + idnormalizer.normalize(filter_value),
                " selected" if selected else "",
                css_modifier(filter_value) if css_modifier else "",
            )

            grouped_results[filter_value] = {
                "title": title,
                "url": url,
                "value": filter_value,
                "css_class": css_class,
                "count": 1,
                "selected": selected,
            }

    # Entry to clear all filters
    urlquery_all = {
        k: v for k, v in list(urlquery.items()) if k not in (idx, idx + "_op")
    }
    if narrow_down and show_count:
        catalog_results = catalog_results_fullcount
    ret = [
        {
            "title": translate(_("subject_all", default=u"All"), context=getRequest()),
            "url": u"{0}/?{1}".format(
                collection_url, urlencode(safe_encode(urlquery_all), doseq=True)
            ),
            "value": "all",
            "css_class": "filterItem filter-all",
            "count": len(catalog_results),
            "selected": idx not in request_params,
        }
    ]

    grouped_results = list(grouped_results.values())

    if callable(sort_key_function):
        grouped_results = sorted(grouped_results, key=sort_key_function)

    ret += grouped_results

    return ret


class ICollectionish(Interface):
    "Adapts object similar to ICollection if has contentlisting tile, or if collection"


@implementer(ICollectionish)
class CollectionishCollection(object):

    def __init__(self, context):
        self.context = context
        self.collection = ICollection(self.context)

    @property
    def query(self):
        return self.collection.query

    @property
    def sort_on(self):
        return self.collection.sort_on

    @property
    def sort_order(self):
        return self.collection.sort_order

    @property
    def sort_reversed(self):
        return self.collection.sort_reversed

    @property
    def limit(self):
        return self.collection.limit

    @property
    def item_count(self):
        return self.collection.item_count

    def results(self, custom_query, request_params):

        # Support for the Event Listing view from plone.app.event
        collection_layout = self.context.getLayout()
        default_view = self.context.restrictedTraverse(collection_layout)
        if isinstance(default_view, EventListing):
            mode = request_params.get("mode", "future")
            date = request_params.get("date", None)
            date = guess_date_from(date) if date else None
            start, end = start_end_from_mode(mode, date, self.collection)
            start, end = _prepare_range(self.collection, start, end)
            custom_query.update(start_end_query(start, end))
            # TODO: expand events. better yet, let collection.results
            #        do that

        return self.collection.results(batch=False, brains=True, custom_query=custom_query)


if ILayoutAware is not None:
    @implementer(ICollectionish)
    @adapter(ILayoutBehaviorAdaptable)
    class CollectionishLayout(CollectionishCollection):
        """Provide interface for either objects with contentlisting tiles or collections or both"""

        tile = None

        def __init__(self, context):
            self.context = context

            la = ILayoutAware(self.context)
            if la.content:
                urls = re.findall('(@@plone.app.standardtiles.contentlisting/[^"]+)', la.content)
                if urls:
                    # TODO: maybe better to get tile data? using ITileDataManager(id)?
                    url = context.REQUEST.response.headers.get('x-tile-url')
                    tile = self.context.unrestrictedTraverse(urls[0])
                    tile.update()
                    if context.REQUEST.response.headers.get('x-tile-url'):
                        if url:
                            context.REQUEST.response.headers['x-tile-url'] = url
                        else:
                            del context.REQUEST.response.headers['x-tile-url']

                    # print(context.REQUEST.response.headers)
                    self.tile = tile
            if self.tile is None:
                # Could still be a ILayoutAware collection
                try:
                    self.collection = ICollection(self.context)
                except TypeError:
                    raise TypeError("No contentlisting tile or Collection found")
            else:
                self.collection = self.tile  # to get properties

        @property
        def sort_reversed(self):
            if self.tile is not None:
                return self.sort_order == "reverse"
            else:
                return self.collection.sort_reversed

        def results(self, custom_query, request_params):
            """Search results"""
            if self.tile is None:
                return super(CollectionishLayout, self).results(custom_query, request_params)

            builder = getMultiAdapter(
                (self.context, self.context.REQUEST), name="querybuilderresults"
            )

            # Include query parameters from request if not set to ignore
            contentFilter = {}
            if not getattr(self.tile, "ignore_request_params", False):
                contentFilter = dict(self.context.REQUEST.get("contentFilter", {}))

            # TODO: handle events extra params

            return builder(
                query=self.query,
                sort_on=self.sort_on or "getObjPositionInParent",
                sort_order=self.sort_order,
                limit=self.limit,
                batch=False,
                brains=True,
                custom_query=custom_query if custom_query is not None else contentFilter,
            )
