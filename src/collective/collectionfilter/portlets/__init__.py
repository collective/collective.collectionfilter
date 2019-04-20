# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import safe_unicode
from plone.app.portlets.portlets.base import Renderer


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
