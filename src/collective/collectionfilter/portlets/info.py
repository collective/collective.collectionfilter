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
    template_type = '__CUSTOM__'
    tag_type = 'H3'
    view_name = None
    content_selector = '#content-core'

    def __init__(
        self,
        header=u"",
        target_collection=None,
        template_type="__CUSTOM__",
        tag_type='H3',
        view_name=None,
        content_selector='#content-core',
    ):
        self.header = header
        self.target_collection = target_collection
        self.template_type = template_type
        self.tag_type = tag_type
        self.view_name = view_name
        self.content_selector = content_selector

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
