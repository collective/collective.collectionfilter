from collective.collectionfilter import _
from collective.collectionfilter.interfaces import ICollectionish
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
from plone.app.event.base import _prepare_range
from plone.app.event.base import guess_date_from
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import start_end_query
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer import idnormalizer
from plone.memoize import ram
from plone.memoize.volatile import DontCache
from urllib.parse import urlencode
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer

import plone.api


try:
    from plone.app.event.browser.event_listing import EventListing
except ImportError:

    class EventListing:
        pass


def _build_url(
    collection_url, urlquery, filter_value, current_idx_value, idx, filter_type
):
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
    return "/".join(
        [
            it
            for it in [collection_url, "?" + query_param if query_param else None]
            if it
        ]
    )


def _build_option(filter_value, url, current_idx_value, groupby_options):
    idx = groupby_options["index"]
    # Optional modifier to set title from filter value
    display_modifier = groupby_options.get("display_modifier", None)
    # CSS modifier to set class on filter item
    css_modifier = groupby_options.get("css_modifier", None)

    # Set title from filter value with modifications,
    # e.g. uuid to title
    title = filter_value
    if filter_value is not EMPTY_MARKER and callable(display_modifier):
        title = display_modifier(filter_value, idx)
        title = safe_decode(title)

    # Set selected state
    selected = filter_value in current_idx_value
    css_class = "filterItem {}{} {}".format(
        "filter-" + idnormalizer.normalize(filter_value),
        " selected" if selected else "",
        css_modifier(filter_value) if css_modifier else "",
    )

    return {
        "title": title,
        "url": url,
        "value": filter_value,
        "css_class": css_class,
        "count": 1,
        "selected": selected,
    }


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
    content_selector="",
    reverse=False,
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
        content_selector,
        reverse,
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
    content_selector="",
    reverse=False,
):
    request_params = request_params or {}
    custom_query = {}  # Additional query to filter the collection

    collection = uuidToObject(target_collection)
    if not collection or not group_by:
        return None
    collection_url = collection.absolute_url()
    option_url = "/".join([it for it in [collection_url, view_name] if it])
    collection = ICollectionish(collection).selectContent(content_selector)
    if (
        collection is None or not collection.content_selector
    ):  # e.g. when no listing tile
        return None

    # Recursively transform all to unicode
    request_params = safe_decode(request_params)

    # Get index in question and the current filter value of this index, if set.
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    idx = groupby_criteria[group_by]["index"]
    current_idx_value = safe_iterable(request_params.get(idx))

    # Additive filtering is about adding other filter values of the same index.
    extra_ignores = [] if narrow_down else [idx, idx + "_op"]

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
    # Value blacklist
    value_blacklist = groupby_criteria[group_by].get("value_blacklist", None) or []
    # Allow value_blacklist to be callables for runtime-evaluation
    value_blacklist = (
        value_blacklist() if callable(value_blacklist) else value_blacklist
    )
    # fallback to title sorted values
    sort_key_function = groupby_criteria[group_by].get(
        "sort_key_function", lambda it: it["title"].lower()
    )

    grouped_results = {}
    for brain in catalog_results:
        # Get filter value
        val = getattr(brain, metadata_attr, None)
        val = val() if callable(val) else val
        # decode it to unicode
        val = safe_decode(val)
        # Make sure it's iterable, as it's the case for e.g. the subject index.
        val = safe_iterable(val)

        for filter_value in val:
            if (
                filter_value is None
                or isinstance(filter_value, Missing)
                or filter_value in value_blacklist
            ):
                continue
            if type(filter_value) is int:
                # if indexed value is an integer, convert to string
                filter_value = str(filter_value)
            if filter_value in grouped_results:
                # Add counter, if filter value is already present
                grouped_results[filter_value]["count"] += 1
                continue

            url = _build_url(
                collection_url=option_url,
                urlquery=urlquery,
                filter_value=filter_value,
                current_idx_value=current_idx_value,
                idx=idx,
                filter_type=filter_type,
            )
            grouped_results[filter_value] = _build_option(
                filter_value=filter_value,
                url=url,
                current_idx_value=current_idx_value,
                groupby_options=groupby_criteria[group_by],
            )

    # Entry to clear all filters
    urlquery_all = {
        k: v for k, v in list(urlquery.items()) if k not in (idx, idx + "_op")
    }
    if narrow_down and show_count:
        # TODO: catalog_results_fullcount is possibly undefined
        catalog_results = catalog_results_fullcount
    ret = [
        {
            "title": translate(
                _("subject_all", default="All"),
                context=getRequest(),
                target_language=plone.api.portal.get_current_language(),
            ),
            "url": "{}/?{}".format(
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

    if reverse:
        grouped_results = reversed(grouped_results)

    ret += grouped_results

    return ret


@implementer(ICollectionish)
class CollectionishCollection:
    def __init__(self, context):
        self.context = context
        self.collection = ICollection(self.context)

    def selectContent(self, selector=""):
        """Collections can only have a single content"""
        return self

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

    @property
    def content_selector(self):
        return "#content-core"  # TODO: could look it up based on view?

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

        return self.collection.results(
            batch=False, brains=True, custom_query=custom_query
        )
