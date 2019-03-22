# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.query import make_query
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.utils import safe_encode
from collective.collectionfilter.vocabularies import DEFAULT_FILTER_TYPE
from collective.collectionfilter.vocabularies import EMPTY_MARKER
from plone.app.contenttypes.behaviors.collection import ICollection
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

import plone.api
import six

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
        view_name='',
        cache_enabled=True,
        request_params=None):
    if not cache_enabled:
        raise DontCache
    cachekey = (
        target_collection,
        group_by,
        filter_type,
        narrow_down,
        view_name,
        request_params,
        ' '.join(plone.api.user.get_roles()),
        plone.api.portal.get_current_language(),
        str(plone.api.portal.get_tool('portal_catalog').getCounter()),
    )
    return cachekey


@ram.cache(_results_cachekey)
def get_filter_items(
        target_collection,
        group_by,
        filter_type=DEFAULT_FILTER_TYPE,
        narrow_down=False,
        view_name='',
        cache_enabled=True,
        request_params=None
):
    request_params = request_params or {}
    custom_query = {}  # Additional query to filter the collection

    collection = uuidToObject(target_collection)
    if not collection or not group_by:
        return None
    collection_url = collection.absolute_url()

    # Recursively transform all to unicode
    request_params = safe_decode(request_params)

    # Support for the Event Listing view from plone.app.event
    collection_layout = collection.getLayout()
    default_view = collection.restrictedTraverse(collection_layout)
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
    if isinstance(current_idx_value, six.string_types):
        # do not expand a string to a list of chars
        current_idx_value = [current_idx_value, ]
    else:
        try:
            current_idx_value = list(current_idx_value)
        except TypeError:
            # int and other stuff
            current_idx_value = [current_idx_value, ]

    extra_ignores = []
    if not narrow_down:
        # Additive filtering is about adding other filter values of the same
        # index.
        extra_ignores = [idx, idx + '_op']
    urlquery = base_query(request_params, extra_ignores)

    # Get all collection results with additional filter defined by urlquery
    custom_query.update(urlquery)
    custom_query = make_query(custom_query)
    catalog_results = ICollection(collection).results(
        batch=False,
        brains=True,
        custom_query=custom_query
    )
    if not catalog_results:
        return None

    # Attribute name for getting filter value from brain
    metadata_attr = groupby_criteria[group_by]['metadata']
    # Optional modifier to set title from filter value
    display_modifier = groupby_criteria[group_by].get('display_modifier', None)
    # Value blacklist
    value_blacklist = groupby_criteria[group_by].get('value_blacklist', None)
    # Allow value_blacklist to be callables for runtime-evaluation
    value_blacklist = value_blacklist() if callable(value_blacklist) else value_blacklist  # noqa
    # fallback to title sorted values
    sort_key_function = groupby_criteria[group_by].get(
        'sort_key_function', lambda it: it['title'].lower())

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
            if value_blacklist and filter_value in value_blacklist:
                # Do not include blacklisted
                continue
            if filter_value in grouped_results:
                # Add counter, if filter value is already present
                grouped_results[filter_value]['count'] += 1
                continue

            # Set title from filter value with modifications,
            # e.g. uuid to title
            title = filter_value
            if filter_value is not EMPTY_MARKER and callable(display_modifier):
                title = _(safe_decode(display_modifier(filter_value)))

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

            query_param = urlencode(safe_encode(_urlquery), doseq=True)
            url = u'/'.join([it for it in [
                collection_url,
                view_name,
                '?' + query_param if query_param else None
            ] if it])

            # Set selected state
            selected = filter_value in current_idx_value

            css_class = 'filterItem {0}{1}'.format(
                'filter-' + idnormalizer.normalize(filter_value),
                ' selected' if selected else ''
            )

            grouped_results[filter_value] = {
                'title': title,
                'url': url,
                'value': filter_value,
                'css_class': css_class,
                'count': 1,
                'selected': selected
            }

    # Entry to clear all filters
    urlquery_all = {
        k: v for k, v in list(urlquery.items()) if k not in (idx, idx + '_op')
    }
    ret = [{
        'title': translate(
            _('subject_all', default=u'All'), context=getRequest()
        ),
        'url': u'{0}/?{1}'.format(
            collection_url,
            urlencode(safe_encode(urlquery_all), doseq=True)
        ),
        'value': 'all',
        'css_class': 'filterItem filter-all',
        'count': len(catalog_results),
        'selected': idx not in request_params
    }]

    grouped_results = list(grouped_results.values())

    if callable(sort_key_function):
        grouped_results = sorted(grouped_results, key=sort_key_function)

    ret += grouped_results

    return ret
