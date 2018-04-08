# -*- coding: utf-8 -*-
from .filteritems import get_filter_items
from .utils import base_query
from .utils import safe_decode
from .utils import safe_encode
from .vocabularies import TEXT_IDX
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.utils import safe_unicode
from urllib import urlencode
from zope.component import queryUtility


class BaseView(object):
    """Abstract base filter view class.
    """
    data = None
    _collection = None

    @property
    def available(self):
        return True

    @property
    def id(self):
        raise NotImplementedError

    @property
    def title(self):
        return self.data.header or self.collection.Title

    @property
    def filterClassName(self):
        name = queryUtility(IIDNormalizer).normalize(self.title)
        return u'filter' + name.capitalize()

    @property
    def reload_url(self):
        raise NotImplementedError

    @property
    def settings(self):
        return self.data

    @property
    def collection(self):
        if not self._collection:
            self._collection = uuidToCatalogBrain(
                self.data.target_collection
            )
        return self._collection


class BaseFilterView(BaseView):

    @property
    def input_type(self):
        if self.data.input_type == 'links':
            return 'link'
        elif self.data.filter_type == 'single':
            if self.data.input_type == 'checkboxes_radiobuttons':
                return 'radio'
            else:
                return 'dropdown'
        else:
            return 'checkbox'

    def results(self):
        results = get_filter_items(
            target_collection=self.data.target_collection,
            group_by=self.data.group_by,
            filter_type=self.data.filter_type,
            narrow_down=self.data.narrow_down,
            cache_time=self.data.cache_time,
            request_params=self.request.form or {}
        )
        return results


class BaseSearchView(BaseView):

    @property
    def value(self):
        return safe_unicode(self.request.get(TEXT_IDX, ''))

    @property
    def action_url(self):
        return self.collection.getURL()

    @property
    def urlquery(self):
        urlquery = {}
        urlquery.update(self.request.form)
        for it in (TEXT_IDX, 'b_start', 'b_size', 'batch', 'sort_on', 'limit'):
            # Remove problematic url parameters
            if it in urlquery:
                del urlquery[it]
        return urlquery

    @property
    def ajax_url(self):
        # Recursively transform all to unicode
        request_params = safe_decode(self.request.form)
        request_params.update({'x': 'y'})  # ensure at least one val is set
        urlquery = base_query(request_params, extra_ignores=['SearchableText'])
        ajax_url = u'{0}/?{1}'.format(
            self.collection.getURL(),
            urlencode(safe_encode(urlquery), doseq=True)
        )
        return ajax_url
