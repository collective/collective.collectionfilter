# -*- coding: utf-8 -*-
from collective.collectionfilter.filteritems import get_filter_items
from collective.collectionfilter.filteritems import get_location_filter_items
from collective.collectionfilter.utils import base_query
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.utils import safe_encode
from collective.collectionfilter.vocabularies import TEXT_IDX
from Acquisition import aq_inner
from collective.collectionfilter import PLONE_VERSION
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.utils import safe_unicode
from six.moves.urllib.parse import urlencode
from zope.component import queryUtility

try:
    from Products.CMFPlone.utils import get_top_request
except ImportError:
    from collective.collectionfilter.utils import get_top_request


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

    @property
    def patCollectionFilter(self):
        if PLONE_VERSION >= '5.1':
            return 'pat-collectionfilter'
        return ''


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
            view_name=self.settings.view_name,
            cache_enabled=self.settings.cache_enabled,
            request_params=self.top_request.form or {}
        )
        return results


class BaseLocationView(BaseView):

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

    def paths(self):
        paths = [{'title':'Home', 'level': 0}]
        params = self.top_request.form or {}
        path = params.get('path', None)
        if path is None:
            return paths
        level = 0
        for path in path.split('/'):
            level += 1
            paths.append({'title': path, 'level': level})
        return paths

    def results(self):
        results = get_location_filter_items(
            target_collection=self.settings.target_collection,
            filter_type=self.settings.filter_type,
            narrow_down=self.settings.narrow_down,
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
        request_params.update({'x': 'y'})  # ensure at least one val is set
        urlquery = base_query(request_params, extra_ignores=['SearchableText'])
        query_param = urlencode(safe_encode(urlquery), doseq=True)
        ajax_url = u'/'.join([it for it in [
            self.collection.getURL(),
            self.settings.view_name,
            '?' + query_param if query_param else None
        ] if it])
        return ajax_url
