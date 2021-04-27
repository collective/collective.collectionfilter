# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseSearchView
from collective.collectionfilter.interfaces import ICollectionSearchSchema
from collective.collectionfilter.portlets import BasePortletRenderer
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


class ICollectionSearchPortlet(ICollectionSearchSchema, IPortletDataProvider):
    """Portlet interface based on ICollectionSearchSchema"""


@implementer(ICollectionSearchPortlet)
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
            return _(u"Collection Search")


class Renderer(BasePortletRenderer, BaseSearchView):
    render = ViewPageTemplateFile("collectionsearch.pt")


class AddForm(base.AddForm):

    schema = ICollectionSearchPortlet
    label = _(u"Add Collection Search Portlet")
    description = _(u"This portlet allows fulltext search in collection results.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = ICollectionSearchPortlet
    label = _(u"Edit Collection Search Portlet")
    description = _(u"This portlet allows fulltext search in collection results.")
