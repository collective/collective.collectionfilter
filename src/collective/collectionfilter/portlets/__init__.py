# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import safe_unicode
from plone.app.portlets.portlets.base import Renderer
from plone import api
from plone.api import env
import json
PLONE_VERSION = env.plone_version()


class BasePortletRenderer(Renderer):

    @property
    def filter_id(self):
        request = get_top_request(self.request)
        portlethash = request.form.get(
            'portlethash',
            getattr(self, '__portlet_metadata__', {}).get('hash', '')
        )
        return portlethash

    @property
    def reload_url(self):
        reload_url = '{0}/@@render-portlet?portlethash={1}'.format(
            self.context.absolute_url(),
            safe_unicode(self.filter_id),
        )
        return reload_url

    @property
    def ajax_load_warning(self):
        ajax_load = self.ajax_load
        if (ajax_load) and PLONE_VERSION < '5.1':
            return True
        return False

    @property
    def ajax_load(self):
        values = api.portal.get_registry_record('plone.patternoptions')
        if 'collectionfilter' in values:
            filterOptions = json.loads(values['collectionfilter'])
            if 'ajaxLoad' in filterOptions:
                return filterOptions['ajaxLoad']
        return not PLONE_VERSION < '5.1'

    @property
    def pat_options(self):

        return json.dumps({
            "collectionUUID": self.settings.target_collection,
            "reloadURL": self.reload_url,
            "ajaxLoad": self.ajax_load,
            "contentSelector": self.settings.content_selector
        })
