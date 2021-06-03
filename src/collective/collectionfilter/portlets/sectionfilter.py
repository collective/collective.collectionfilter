# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseSectionView
from collective.collectionfilter.interfaces import ICollectionSectionFilterSchema
from collective.collectionfilter.portlets import BasePortletRenderer
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


try:
    from Products.CMFPlone.utils import get_top_request
except ImportError:
    from collective.collectionfilter.utils import get_top_request


class ICollectionSectionPortlet(
    ICollectionSectionFilterSchema, IPortletDataProvider
):
    """Portlet interface based on ICollectionSectionFilterSchema"""


@implementer(ICollectionSectionPortlet)
class Assignment(base.Assignment):

    header = u""
    target_collection = None
    view_name = None
    content_selector = "#content-core"

    def __init__(
        self,
        header=u"",
        target_collection=None,
        view_name=None,
        content_selector="#content-core",
        show_count=False,
        cache_enabled=True,
    ):
        self.header = header
        self.target_collection = target_collection
        self.view_name = view_name
        self.content_selector = content_selector
        self.show_count = show_count
        self.cache_enabled = cache_enabled

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u"Collection Section Filter")


class Renderer(BasePortletRenderer, BaseSectionView):
    render = ViewPageTemplateFile("sectionfilter.pt")

    @property
    def filter_id(self):
        request = get_top_request(self.request)
        portlethash = request.form.get(
            "portlethash",
            getattr(self, "__portlet_metadata__", {}).get("hash", ""),
        )
        return portlethash

    @property
    def reload_url(self):
        reload_url = "{0}/@@render-portlet?portlethash={1}".format(
            self.context.absolute_url(), self.filter_id
        )
        return reload_url


class AddForm(base.AddForm):
    schema = ICollectionSectionFilterSchema
    label = _(u"Add Collection Section Filter Portlet")
    description = _(
        u"This portlet allows filtering of collection results based on their"
        u"position in the site."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    schema = ICollectionSectionFilterSchema
    label = _(u"Edit Collection Section Filter Portlet")
    description = _(
        u"This portlet allows filtering of collection results based on their"
        u"position in the site."
    )
