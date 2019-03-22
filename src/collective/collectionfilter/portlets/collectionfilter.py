# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import get_top_request
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseFilterView
from collective.collectionfilter.interfaces import ICollectionFilterSchema
from collective.collectionfilter.vocabularies import DEFAULT_FILTER_TYPE
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implementer


class ICollectionFilterPortlet(ICollectionFilterSchema, IPortletDataProvider):
    """Portlet interface based on ICollectionFilterSchema
    """


@implementer(ICollectionFilterPortlet)
class Assignment(base.Assignment):

    header = u""
    target_collection = None
    group_by = u""
    show_count = False
    cache_enabled = True
    filter_type = DEFAULT_FILTER_TYPE
    input_type = 'links'
    narrow_down = False
    view_name = None
    content_selector = '#content-core'
    # list_scaling = None

    def __init__(
        self,
        header=u"",
        target_collection=None,
        group_by=u"",
        show_count=False,
        cache_enabled=True,
        filter_type=DEFAULT_FILTER_TYPE,
        input_type='links',
        narrow_down=False,
        view_name=None,
        content_selector='#content-core',
        # list_scaling=None
    ):
        self.header = header
        self.target_collection = target_collection
        self.group_by = group_by
        self.show_count = show_count
        self.cache_enabled = cache_enabled
        self.filter_type = filter_type
        self.input_type = input_type
        self.narrow_down = narrow_down
        self.view_name = view_name
        self.content_selector = content_selector
        # self.list_scaling = list_scaling

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
            return _(u'Collection Filter')


class Renderer(base.Renderer, BaseFilterView):
    render = ViewPageTemplateFile('collectionfilter.pt')

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

    schema = ICollectionFilterPortlet
    label = _(u"Add Collection Filter Portlet")
    description = _(
        u"This portlet shows grouped criteria of collection results and "
        u"allows filtering of collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = ICollectionFilterPortlet
    label = _(u"Edit Collection Filter Portlet")
    description = _(
        u"This portlet shows grouped criteria of collection results and "
        u"allows filtering of collection results."
    )
