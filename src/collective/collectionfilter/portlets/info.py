# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseInfoView
from collective.collectionfilter.interfaces import ICollectionFilterInfo  # noqa
from collective.collectionfilter.portlets import BasePortletRenderer
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implementer


class ICollectionFilterInfoPortlet(ICollectionFilterInfo, IPortletDataProvider):  # noqa
    """Portlet interface based on ICollectionFilterSchema
    """


@implementer(ICollectionFilterInfoPortlet)
class Assignment(base.Assignment):

    header = u""
    target_collection = None
    view_name = None
    content_selector = '#content-core'
    template_type = []
    hide_when = []
    as_links = True

    def __init__(
        self,
        header=u"",
        target_collection=None,
        view_name=None,
        content_selector='#content-core',
        template_type=[],
        hide_when=[],
        as_links=True,
    ):
        self.header = header
        self.target_collection = target_collection
        self.view_name = view_name
        self.content_selector = content_selector
        self.template_type = template_type
        self.hide_when = hide_when
        self.as_links = as_links

    @property
    def portlet_id(self):
        """Return the portlet assignment's unique object id.
        """
        return id(self)

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u'Collection Filter Search Info')


class Renderer(BasePortletRenderer, BaseInfoView):
    render = ViewPageTemplateFile('info.pt')


class AddForm(base.AddForm):

    schema = ICollectionFilterInfoPortlet
    label = _(u"Add Collection Filter Info Portlet")
    description = _(
        u"This portlet shows information about the filter selected"
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = ICollectionFilterInfoPortlet
    label = _(u"Edit Collection Filter Info Portlet")
    description = _(
        u"This portlet shows information about the filter selected"
    )
