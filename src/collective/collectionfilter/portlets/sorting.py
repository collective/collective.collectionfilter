# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseSortOnView
from collective.collectionfilter.interfaces import (  # noqa
    ICollectionFilterResultListSort,
)
from collective.collectionfilter.portlets import BasePortletRenderer
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


class ICollectionFilterSortOnPortlet(
    ICollectionFilterResultListSort, IPortletDataProvider
):  # noqa
    """Portlet interface based on ICollectionFilterSchema"""


@implementer(ICollectionFilterSortOnPortlet)
class Assignment(base.Assignment):

    header = u""
    target_collection = None
    view_name = None
    sort_on = u""
    input_type = "links"
    content_selector = "#content-core"

    def __init__(
        self,
        header=u"",
        target_collection=None,
        sort_on=u"",
        input_type="links",
        view_name=None,
        content_selector="#content-core",
    ):
        self.header = header
        self.target_collection = target_collection
        self.sort_on = sort_on
        self.input_type = input_type
        self.view_name = view_name
        self.content_selector = content_selector

    @property
    def portlet_id(self):
        """Return the portlet assignment's unique object id."""
        return id(self)

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u"Collection Result Sorting")


class Renderer(BasePortletRenderer, BaseSortOnView):
    render = ViewPageTemplateFile("sorting.pt")


class AddForm(base.AddForm):

    schema = ICollectionFilterSortOnPortlet
    label = _(u"Add Collection Result Listing Sort Portlet")
    description = _(u"This portlet shows sorting options for the result listing.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = ICollectionFilterSortOnPortlet
    label = _(u"Edit Collection Result Listing Sort Portlet")
    description = _(u"This portlet shows sorting options for the result listing.")
