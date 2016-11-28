from . import msgFact as _
from .utils import safe_decode
from .utils import safe_encode
from .vocabularies import EMPTY_MARKER
from .vocabularies import GROUPBY_CRITERIA
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.event.base import _prepare_range
from plone.app.event.base import guess_date_from
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import start_end_query
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.memoize import ram
from plone.memoize.volatile import DontCache
from plone.portlets.interfaces import IPortletDataProvider
from time import time
from urllib import urlencode
from zope import schema
from zope.interface import implements

try:
    from plone.app.event.browser.event_listing import EventListing
except ImportError:
    class EventListing(object):
        pass

PLONE5 = getFSVersionTuple()[0] >= 5

if PLONE5:
    base_AddForm = base.AddForm
    base_EditForm = base.EditForm
else:
    from plone.app.portlets.browser.z3cformhelper import AddForm as base_AddForm  # noqa
    from plone.app.portlets.browser.z3cformhelper import EditForm as base_EditForm  # noqa
    from z3c.form import field


def _results_cachekey(method, self, collection, request_params):
    cache_time = int(self.data.cache_time)
    if not cache_time:
        # Don't cache on cache_time = 0 or any other falsy value
        raise DontCache
    context = aq_inner(self.context)
    path = '/'.join(context.getPhysicalPath())
    portal_membership = getToolByName(context, 'portal_membership')
    timeout = time() // int(self.data.cache_time)
    cachekey = (
        self.data.portlet_id,
        path,
        portal_membership.getAuthenticatedMember().id,
        timeout,
        request_params
    )
    return cachekey


@ram.cache(_results_cachekey)
def _results(self, collection, request_params):
    ret = []
    if collection:
        collection_layout = collection.getLayout()
        default_view = collection.restrictedTraverse(collection_layout)
        results = []
        custom_query = {}
        if isinstance(default_view, EventListing):
            mode = request_params.get('mode', 'future')
            date = request_params.get('date', None)
            date = guess_date_from(date) if date else None

            start, end = start_end_from_mode(mode, date, collection)
            start, end = _prepare_range(collection, start, end)
            custom_query.update(start_end_query(start, end))
            # TODO: expand events. better yet, let collection.results
            #       do that

        idx = GROUPBY_CRITERIA[self.data.group_by]['index']
        urlquery = {}
        urlquery.update(request_params)
        ignore_params = [
            'b_start',
            'b_size',
            'batch',
            'sort_on',
            'limit'
        ] + [idx] if self.data.additive_filter else []

        for it in ignore_params:
            # Remove unwanted url parameters
            if it in urlquery:
                del urlquery[it]

        custom_query.update(urlquery)
        results = collection.results(
            batch=False, custom_query=custom_query
        )

        if results:

            ret.append(dict(
                title=_('subject_all', default=u'All'),
                url=u'{0}/?{1}'.format(
                    self.collection.absolute_url(),
                    urlencode(urlquery)
                ),
                count=len(results),
                selected=idx not in request_params
            ))

            attr = GROUPBY_CRITERIA[self.data.group_by]['metadata']
            mod = GROUPBY_CRITERIA[self.data.group_by]['display_modifier']

            grouped_results = {}
            for item in results:
                val = getattr(item, attr, None)
                if callable(val):
                    val = val()
                if not getattr(val, '__iter__', False):
                    val = [val]
                for crit in val:
                    if crit not in grouped_results:
                        urlquery[idx] = crit
                        title = _(safe_decode(
                            mod(crit)
                            if mod and crit is not EMPTY_MARKER
                            else crit
                        ))  # mod modifies for displaying (e.g. uuid to title)  # noqa
                        url = u'{0}/?{1}'.format(
                            self.collection.absolute_url(),
                            urlencode(safe_encode(urlquery))  # need to be utf-8 encoded  # noqa
                        )
                        selected = safe_decode(request_params.get(idx)) == safe_decode(crit)  # noqa
                        sort_key = crit if crit else 'zzzzzz'
                        crit_dict = {
                            'sort_key': sort_key.lower(),
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


