# -*- coding: utf-8 -*-
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

try:
    from plone.app.blocks.layoutbehavior import ILayoutAware
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
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer

import plone.api
import six
import re
from collections import OrderedDict


try:
    from plone.app.event.browser.event_listing import EventListing
except ImportError:

    class EventListing(object):
        pass


def _build_url(
    collection_url, urlquery, filter_value, current_idx_value, idx, filter_type, allow_all_for_first_option=True
):
    # Build filter url query
    _urlquery = urlquery.copy()
    # Allow deselection
    if filter_value in current_idx_value:
        _urlquery[idx] = [it for it in current_idx_value if it != filter_value and not allow_all_for_first_option]
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
    css_class = "filterItem {0}{1} {2}".format(
        "filter-" + idnormalizer.normalize(filter_value),
        " selected" if selected else "",
        css_modifier(filter_value) if css_modifier else "",
    )

    # HACK: Only used by dropdowns currently as they don't support css styles
    level = int(next(iter(re.findall(r"pathLevel(\d+)", css_class)), 0))

    return {
        "title": title,
        "url": url,
        "value": filter_value,
        "css_class": css_class,
        "count": 1,
        "selected": selected,
        "level": level
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
    include_all_option=True,
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
        include_all_option,
        " ".join(plone.api.user.get_roles()),
        plone.api.portal.get_current_language(),
        str(plone.api.portal.get_tool("portal_catalog").getCounter()),
    )
    return cachekey


def _section_results_cachekey(
    method, target_collection, view_name, cache_enabled, request_params
):
    if not cache_enabled:
        raise DontCache
    cachekey = (
        target_collection,
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
    content_selector="",
    include_all_option=True,
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
    # Things break if sort_order is not a str
    if six.PY2 and "sort_order" in request_params:
        request_params["sort_order"] = str(request_params["sort_order"])

    # Get index in question and the current filter value of this index, if set.
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    idx = groupby_criteria[group_by]["index"]
    current_idx_value = safe_iterable(request_params.get(idx))

    # Additive filtering is about adding other filter values of the same index.
    extra_ignores = [] if narrow_down else [idx, idx + "_op"]

    urlquery = base_query(request_params, extra_ignores)

    # Optional modifier to sort results so filters displayed in the correct order
    sort_on = groupby_criteria[group_by].get("sort_on", None)

    # Get all collection results with additional filter defined by urlquery
    custom_query.update(urlquery)
    if sort_on is not None:
        custom_query['sort_on'] = sort_on
    custom_query = make_query(custom_query)

    catalog_results = collection.results(custom_query, request_params)
    if not catalog_results:
        return None
    catalog_results_fullcount = len(catalog_results)
    if narrow_down and show_count:
        # we need the extra_ignores to get a true count
        # even when narrow_down filters the display of indexed values
        # count_query allows us to do that true count
        count_query = {}
        count_urlquery = base_query(request_params, [idx, idx + "_op"])
        count_query.update(count_urlquery)
        catalog_results_fullcount = len(collection.results(count_query, request_params))

    # Attribute name for getting filter value from brain
    metadata_attr = groupby_criteria[group_by]["metadata"]
    # Optional modifier to modify the metadata value into one or more groupby values
    groupby_modifier = groupby_criteria[group_by].get("groupby_modifier", None)
    if not groupby_modifier:
        def groupby_modifier(values, cur, narrow):
            return values
    # Value blacklist
    value_blacklist = groupby_criteria[group_by].get("value_blacklist", None) or []
    # Allow value_blacklist to be callables for runtime-evaluation
    value_blacklist = (value_blacklist() if callable(value_blacklist) else value_blacklist) or []

    # fallback to title sorted values
    sort_key_function = None if sort_on else groupby_criteria[group_by].get(
        "sort_key_function", lambda it: it["title"].lower()
    )

    # ensure all values associated with current selection are selected
    selected_values = current_idx_value + list(groupby_modifier(current_idx_value, current_idx_value, narrow_down))

    grouped_results = OrderedDict()
    for brain in catalog_results:

        # Get filter value
        val = getattr(brain, metadata_attr, None)
        val = val() if callable(val) else val
        # decode it to unicode
        val = safe_decode(val)
        # Make sure it's iterable, as it's the case for e.g. the subject index.
        vals = safe_iterable(val)
        # allow excluding or extending the value per index
        vals = groupby_modifier(vals, current_idx_value, narrow_down)

        for filter_value in vals:
            if (
                filter_value is None
                or isinstance(filter_value, Missing)
                or filter_value in value_blacklist
            ):
                continue
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
                allow_all_for_first_option=include_all_option
            )
            grouped_results[filter_value] = _build_option(
                filter_value=filter_value,
                url=url,
                current_idx_value=selected_values,
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
                _("subject_all", default=u"All"),
                context=getRequest(),
                target_language=plone.api.portal.get_current_language(),
            ),
            "url": u"{0}/?{1}".format(
                collection_url, urlencode(safe_encode(urlquery_all), doseq=True)
            ),
            "value": "all",
            "css_class": "filterItem filter-all",
            "count": catalog_results_fullcount,
            "selected": idx not in request_params,
            "level": 0
        }
    ] if include_all_option else []

    grouped_results = list(grouped_results.values())
    ret += sorted(grouped_results, key=sort_key_function) if callable(sort_key_function) else grouped_results
    return ret


def _build_url(collection_url, urlquery, filter_value, current_idx_value, idx, filter_type):
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
    url = "/".join([it for it in [collection_url, "?" + query_param if query_param else None] if it])
    return url


@ram.cache(_section_results_cachekey)
def get_section_filter_items(
    target_collection, view_name="", cache_enabled=True, request_params=None
):
    request_params = request_params or {}
    custom_query = {}  # Additional query to filter the collection

    collection = uuidToObject(target_collection)
    if not collection:
        return None
    collection_url = collection.absolute_url()
    collection_layout = collection.getLayout()
    default_view = collection.restrictedTraverse(collection_layout)

    # Recursively transform all to unicode
    request_params = safe_decode(request_params)

    # Support for the Event Listing view from plone.app.event
    if isinstance(default_view, EventListing):
        mode = request_params.get("mode", "future")
        date = request_params.get("date", None)
        date = guess_date_from(date) if date else None
        start, end = start_end_from_mode(mode, date, collection)
        start, end = _prepare_range(collection, start, end)
        custom_query.update(start_end_query(start, end))
        # TODO: expand events. better yet, let collection.results
        #       do that

    current_path_value = request_params.get("path")
    urlquery = base_query(request_params, ["path"])

    # Get all collection results with additional filter defined by urlquery
    custom_query.update(urlquery)
    custom_query = make_query(custom_query)
    catalog_results = ICollection(collection).results(
        batch=False, brains=True, custom_query=custom_query
    )

    # Entry to clear all filters
    urlquery_all = {k: v for k, v in urlquery.items() if k != "path"}
    ret = [
        {
            "title": translate(
                _("location_home", default=u"Home"), context=getRequest()
            ),
            "url": u"{0}/?{1}".format(
                collection_url, urlencode(safe_encode(urlquery_all), doseq=True)
            ),
            "value": "all",
            "css_class": "navTreeItem filterItem filter-all selected",
            "count": len(catalog_results),
            "level": 0,
            "contenttype": "folder",
        }
    ]

    if not catalog_results:
        return ret

    portal = plone.api.portal.get()
    portal_path = portal.getPhysicalPath()
    qspaths = current_path_value and current_path_value.split("/") or []
    filtered_path = "/".join(list(portal_path) + qspaths)
    grouped_results = {}
    level = len(qspaths) + 1
    for brain in catalog_results:

        # Get path, remove portal root from path, remove leading /
        path = brain.getPath()
        if path.startswith(filtered_path):
            path = path[len(filtered_path) + 1 :]  # noqa: E203
        else:
            continue

        # If path is in the root, don't add anything to path
        paths = path.split("/")
        if len(paths) == 1:
            continue

        first_path = paths[0]
        if first_path in grouped_results:
            # Add counter, if path is already present
            grouped_results[first_path]["count"] += 1
            continue

        title = first_path
        ctype = "folder"
        container = portal.portal_catalog.searchResults(
            {
                "path": {
                    "query": "/".join(
                        list(portal.getPhysicalPath()) + qspaths + [first_path]
                    ),
                    "depth": 0,
                }
            }
        )
        if len(container) > 0:
            title = container[0].Title
            ctype = container[0].portal_type.lower()

        # Build filter url query
        _urlquery = urlquery.copy()
        _urlquery["path"] = "/".join(qspaths + [first_path])
        query_param = urlencode(safe_encode(_urlquery), doseq=True)
        url = u"/".join(
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

        css_class = "navTreeItem filterItem {0}".format(
            "filter-" + idnormalizer.normalize(first_path)
        )

        grouped_results[first_path] = {
            "title": title,
            "url": url,
            "value": first_path,
            "css_class": css_class,
            "count": 1,
            "level": level,
            "contenttype": ctype,
        }

    # Add the selected paths
    item = portal
    level = 0
    for path in qspaths:
        item = item.get(path, None)
        if not item:
            break

        # Get the results just in this subfolder
        item_path = "/".join(item.getPhysicalPath())[
            len("/".join(portal_path)) + 1 :  # noqa: 203
        ]
        custom_query = {"path": item_path}
        custom_query.update(urlquery)
        custom_query = make_query(custom_query)
        catalog_results = ICollection(collection).results(
            batch=False, brains=True, custom_query=custom_query
        )
        level += 1
        _urlquery = urlquery.copy()
        _urlquery["path"] = "/".join(qspaths[: qspaths.index(path) + 1])
        query_param = urlencode(safe_encode(_urlquery), doseq=True)
        url = u"/".join(
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
        ret.append(
            {
                "title": item.Title(),
                "url": url,
                "value": path,
                "css_class": "filter-%s selected"
                % idnormalizer.normalize(path),
                "count": len(catalog_results),
                "level": level,
                "contenttype": item.portal_type.lower(),
            }
        )

    grouped_results = grouped_results.values()

    # TODO: sortable option, probably should just sort by position in container
    # if callable(sort_key_function):
    #    grouped_results = sorted(grouped_results, key=sort_key_function)

    ret += grouped_results

    return ret


@implementer(ICollectionish)
class CollectionishCollection(object):
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
        return u"#content-core"  # TODO: could look it up based on view?

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
