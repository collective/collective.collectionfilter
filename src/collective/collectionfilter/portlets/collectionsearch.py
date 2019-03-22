# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseSearchView
from collective.collectionfilter.interfaces import ICollectionSearchSchema
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implementer


class ICollectionSearchPortlet(ICollectionSearchSchema, IPortletDataProvider):
    """Portlet interface based on ICollectionSearchSchema
    """


@implementer(ICollectionSearchPortlet)
class Assignment(base.Assignment):

    header = u""
    target_collection = None
    view_name = None
    content_selector = '#content-core'

    def __init__(
        self,
        header=u"",
        target_collection=None,
        view_name=None,
        content_selector='#content-core',
    ):
        self.header = header
        self.target_collection = target_collection
        self.view_name = view_name
        self.content_selector = content_selector

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u'Collection Search')


class Renderer(base.Renderer, BaseSearchView):
    render = ViewPageTemplateFile('collectionsearch.pt')

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


class AddForm(base.AddForm):

    schema = ICollectionSearchPortlet
    label = _(u"Add Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = ICollectionSearchPortlet
    label = _(u"Edit Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )
