from . import _
from .interfaces import IGroupByCriteria
from .utils import safe_decode
from .utils import safe_encode
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

import plone.api

try:
    from plone.app.event.browser.event_listing import EventListing
except ImportError:
    class EventListing(object):
        pass


def _results_cachekey(
        method,
        target_collection_uid,
        group_by,
        additive_filter,
        cache_time,
        request_params):
    cache_time = int(cache_time)
    if not cache_time:
        # Don't cache on cache_time = 0 or any other falsy value
        raise DontCache
    timeout = time() // int(cache_time)
    cachekey = (
        target_collection_uid,
        group_by,  # TODO: group_by.items() & sort
        additive_filter,
        request_params,  # TODO: request_params.items() & sort
        getattr(plone.api.user.get_current(), 'id', ''),
        timeout
    )
    return cachekey


@ram.cache(_results_cachekey)
def get_filter_items(
        target_collection_uid,
        group_by,
        additive_filter=False,
        cache_time=3600,
        request_params={}
):
    ret = []

    collection = uuidToObject(target_collection_uid)
    if not collection:
        return ret

    collection_url = collection.absolute_url()
    results = []
    custom_query = {}

    # Support for the Event Listing view from plone.app.event
    # TODO: Removal canditate
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

    groupby_criteria = getUtility(IGroupByCriteria)()
    idx = groupby_criteria[group_by]['index']
    urlquery = {}
    urlquery.update(request_params)
    ignore_params = [
        'b_start',
        'b_size',
        'batch',
        'sort_on',
        'limit',
        'portlethash'
    ]

    if not additive_filter:
        ignore_params += [idx]

    for it in ignore_params:
        # Remove unwanted url parameters
        if it in urlquery:
            del urlquery[it]

    custom_query.update(urlquery)
    results = collection.results(
        batch=False, custom_query=custom_query
    )

    if results:

        urlquery_all = urlquery.copy()
        if idx in urlquery_all:
            # Be sure to be able to clear filters
            del urlquery_all[idx]
        ret.append(dict(
            title=_('subject_all', default=u'All'),
            url=u'{0}/?{1}'.format(
                collection_url,
                urlencode(urlquery_all)
            ),
            count=len(results),
            selected=idx not in request_params
        ))

        attr = groupby_criteria[group_by]['metadata']
        mod = groupby_criteria[group_by]['display_modifier']

        grouped_results = {}
        for item in results:
            val = getattr(item, attr, None)
            if callable(val):
                val = val()
            if not getattr(val, '__iter__', False):
                val = [val]
            for crit in val:
                if crit not in grouped_results:
                    title = _(safe_decode(
                        mod(crit)
                        if mod and crit is not EMPTY_MARKER
                        else crit
                    ))  # mod modifies for displaying (e.g. uuid to title)

                    current_idx_value = safe_decode(request_params.get(idx))
                    selected = False
                    if isinstance(current_idx_value, list):
                        selected = safe_decode(crit) in current_idx_value
                    elif current_idx_value is not None:
                        selected = safe_decode(crit) == current_idx_value

                    _urlquery = urlquery.copy()
                    _urlquery[idx] = crit
                    if additive_filter and current_idx_value != safe_decode(crit):
                        if isinstance(current_idx_value, list):
                            _urlquery[idx] = current_idx_value + [crit]
                        elif current_idx_value is not None:
                            _urlquery[idx] = [current_idx_value, crit]

                    url = u'{0}/?{1}'.format(
                        collection_url,
                        urlencode(safe_encode(_urlquery), True)
                    )

                    crit_dict = {
                        'sort_key': crit.lower(),
                        'count': 1,
                        'title': title,
                        'url': url,
                        'selected': selected
                    }
                    grouped_results[crit] = crit_dict

                else:
                    grouped_results[crit]['count'] += 1

        ret += sorted(
            grouped_results.values(),
            key=lambda it: it['sort_key']
        )

    return ret
