# -*- coding: utf-8 -*-
from .. import _
from ..baseviews import BaseSearchView
from ..interfaces import ICollectionSearchSchema
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


class ICollectionSearchPortlet(ICollectionSearchSchema, IPortletDataProvider):
    """Portlet interface based on ICollectionSearchSchema
    """


@implementer(ICollectionSearchPortlet)
class Assignment(base.Assignment):

    header = u""
    target_collection = None

    def __init__(
        self,
        header=u"",
        target_collection=None,
    ):
        self.header = header
        self.target_collection = target_collection

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u'Collection Search')


class Renderer(BaseSearchView, base.Renderer):
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
            self.filter_id
        )
        return reload_url


class AddForm(base_AddForm):
    if PLONE5:
        schema = ICollectionSearchPortlet
    else:
        fields = field.Fields(ICollectionSearchPortlet)

    label = _(u"Add Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base_EditForm):
    if PLONE5:
        schema = ICollectionSearchPortlet
    else:
        fields = field.Fields(ICollectionSearchPortlet)

    label = _(u"Edit Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )
