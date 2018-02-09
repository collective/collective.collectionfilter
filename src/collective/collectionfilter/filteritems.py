# -*- coding: utf-8 -*-
from . import _
from .interfaces import IGroupByCriteria
from .query import make_query
from .utils import base_query
from .utils import safe_decode
from .utils import safe_encode
from .vocabularies import DEFAULT_FILTER_TYPE
from .vocabularies import EMPTY_MARKER
from plone.app.event.base import _prepare_range
from plone.app.event.base import guess_date_from
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import start_end_query
from plone.app.uuid.utils import uuidToObject
from plone.memoize import ram
from plone.memoize.volatile import DontCache
from time import time
from urllib import urlencode
from zope.component import getUtility
from zope.i18n import translate
from zope.globalrequest import getRequest

import plone.api


try:
    from plone.app.event.browser.event_listing import EventListing
except ImportError:
    class EventListing(object):
        pass


def _results_cachekey(
        method,
        target_collection,
        group_by,
        filter_type,
        narrow_down,
        cache_time,
        request_params):
    cache_time = int(cache_time)
    if not cache_time:
        # Don't cache on cache_time = 0 or any other falsy value
        raise DontCache
    timeout = time() // int(cache_time)
    cachekey = (
        target_collection,
        group_by,
        filter_type,
        narrow_down,
        request_params,
        # hash(frozenset(request_params.items())),
        getattr(plone.api.user.get_current(), 'id', ''),
        timeout
    )
    return cachekey


@ram.cache(_results_cachekey)
def get_filter_items(
        target_collection,
        group_by,
        filter_type=DEFAULT_FILTER_TYPE,
        narrow_down=False,
        cache_time=3600,
        request_params={}
):
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
        mode = request_params.get('mode', 'future')
        date = request_params.get('date', None)
        date = guess_date_from(date) if date else None
        start, end = start_end_from_mode(mode, date, collection)
        start, end = _prepare_range(collection, start, end)
        custom_query.update(start_end_query(start, end))
        # TODO: expand events. better yet, let collection.results
        #       do that

    # Get index in question and the current filter value of this index, if set.
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    idx = groupby_criteria[group_by]['index']
    current_idx_value = request_params.get(idx)
    if not getattr(current_idx_value, '__iter__', False):
        current_idx_value = [current_idx_value] if current_idx_value else []

    extra_ignores = []
    if not narrow_down:
        # Additive filtering is about adding other filter values of the same
        # index.
        extra_ignores = [idx, idx + '_op']
    urlquery = base_query(request_params, extra_ignores)

    # Get all collection results with additional filter defined by urlquery
    custom_query.update(urlquery)
    catalog_results = collection.results(
        batch=False,
        brains=True,
        custom_query=make_query(custom_query)
    )
    if not catalog_results:
        return None

    # Attribute name for getting filter value from brain
    metadata_attr = groupby_criteria[group_by]['metadata']
    # Optional modifier to set title from filter value
    display_modifier = groupby_criteria[group_by]['display_modifier']
    grouped_results = {}
    for brain in catalog_results:

        # Get filter value
        val = getattr(brain, metadata_attr, None)
        if callable(val):
            val = val()
        # Make sure it's iterable, as it's the case for e.g. the subject index.
        if not getattr(val, '__iter__', False):
            val = [val]
        val = safe_decode(val)

        for filter_value in val:
            if not filter_value:
                continue
            # Add counter, if filter value is already present
            if filter_value in grouped_results:
                grouped_results[filter_value]['count'] += 1
                continue

            # Set title from filter value with modifications,
            # e.g. uuid to title
            title = _(safe_decode(
                display_modifier(filter_value)
                if display_modifier and filter_value is not EMPTY_MARKER
                else filter_value
            ))

            # Build filter url query
            _urlquery = urlquery.copy()
            # Allow deselection
            if filter_value in current_idx_value:
                _urlquery[idx] = [
                    it for it in current_idx_value if it != filter_value
                ]
            elif filter_type != 'single':
                # additive filter behavior
                _urlquery[idx] = current_idx_value + [filter_value]
                _urlquery[idx + '_op'] = filter_type  # additive operator
            else:
                _urlquery[idx] = filter_value
            url = u'{0}/?{1}'.format(
                collection_url,
                urlencode(safe_encode(_urlquery), doseq=True)
            )

            # Set selected state
            selected = filter_value in current_idx_value

            grouped_results[filter_value] = {
                'sort_key': filter_value.lower(),
                'title': title,
                'url': url,
                'value': filter_value,
                'count': 1,
                'selected': selected
            }

    # Entry to clear all filters
    urlquery_all = {
        k: v for k, v in urlquery.items() if k not in (idx, idx + '_op')
    }
    ret = [{
        'title': translate(_('subject_all', default=u'All'), context=getRequest()),
        'url': u'{0}/?{1}'.format(
            collection_url,
            urlencode(safe_encode(urlquery_all), doseq=True)
        ),
        'value': 'all',
        'count': len(catalog_results),
        'selected': idx not in request_params
    }]

    ret += sorted(
        grouped_results.values(),
        key=lambda it: it['sort_key']
    )

    return ret
