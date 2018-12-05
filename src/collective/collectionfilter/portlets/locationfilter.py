# -*- coding: utf-8 -*-
from .. import _
from ..baseviews import BaseLocationView
from ..interfaces import ICollectionLocationFilterSchema
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility
from zope.interface import implementer


PLONE5 = getFSVersionTuple()[0] >= 5

if PLONE5:
    base_AddForm = base.AddForm
    base_EditForm = base.EditForm
else:
    from plone.app.portlets.browser.z3cformhelper import AddForm as base_AddForm  # noqa
    from plone.app.portlets.browser.z3cformhelper import EditForm as base_EditForm  # noqa
    from z3c.form import field


class ICollectionLocationPortlet(ICollectionLocationFilterSchema,
                                   IPortletDataProvider):
    """Portlet interface based on ICollectionLocationFilterSchema
    """


@implementer(ICollectionLocationPortlet)
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
        show_count=False,
        cache_enabled=True
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
            return _(u'Collection Location Filter')


class Renderer(base.Renderer, BaseLocationView):
    render = ViewPageTemplateFile('locationfilter.pt')

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
            self.filter_id
        )
        return reload_url


class AddForm(base_AddForm):
    if PLONE5:
        schema = ICollectionLocationFilterSchema
    else:
        fields = field.Fields(ICollectionLocationFilterSchema)

    label = _(u"Add Collection Location Filter Portlet")
    description = _(
        u"This portlet allows filtering of collection results based on their"
        u"position in the site."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base_EditForm):
    if PLONE5:
        schema = ICollectionLocationFilterSchema
    else:
        fields = field.Fields(ICollectionLocationFilterSchema)

    label = _(u"Edit Collection Location Filter Portlet")
    description = _(
        u"This portlet allows filtering of collection results based on their"
        u"position in the site."
    )
