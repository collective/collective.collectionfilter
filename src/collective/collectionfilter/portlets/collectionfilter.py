# -*- coding: utf-8 -*-
from .. import _
from ..filteritems import get_filter_items
from ..interfaces import ICollectionFilterSchema
from ..vocabularies import DEFAULT_FILTER_TYPE
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.interface import implements


PLONE5 = getFSVersionTuple()[0] >= 5

if PLONE5:
    base_AddForm = base.AddForm
    base_EditForm = base.EditForm
else:
    from plone.app.portlets.browser.z3cformhelper import AddForm as base_AddForm  # noqa
    from plone.app.portlets.browser.z3cformhelper import EditForm as base_EditForm  # noqa
    from z3c.form import field


class ICollectionFilterPortlet(ICollectionFilterSchema, IPortletDataProvider):
    """Portlet interface based on ICollectionFilterSchema
    """
    header = schema.TextLine(
        title=_('label_header', default=u'Portlet header'),
        description=_(
            'help_header',
            u'Title of the rendered portlet.'
        ),
        required=False,
    )


class Assignment(base.Assignment):
    implements(ICollectionFilterPortlet)

    header = u""
    target_collection = None
    group_by = u""
    show_count = False
    cache_time = 60
    filter_type = DEFAULT_FILTER_TYPE
    input_type = 'links'
    narrow_down = False
    # list_scaling = None

    def __init__(
        self,
        header=u"",
        target_collection=None,
        group_by=u"",
        show_count=False,
        cache_time=60,
        filter_type=DEFAULT_FILTER_TYPE,
        input_type='links',
        narrow_down=False,
        # list_scaling=None
    ):
        self.header = header
        self.target_collection = target_collection
        self.group_by = group_by
        self.show_count = show_count
        self.cache_time = cache_time
        self.filter_type = filter_type
        self.input_type = input_type
        self.narrow_down = narrow_down
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


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('collectionfilter.pt')

    @property
    def available(self):
        return True

    @property
    def id(self):
        portlethash = self.request.form.get(
            'portlethash',
            getattr(self, '__portlet_metadata__', {}).get('hash', '')
        )
        return portlethash

    @property
    def title(self):
        title = self.data.header or\
            uuidToCatalogBrain(self.data.target_collection).Title
        return title

    @property
    def filterClassName(self):
        if self.data.header:
            name = queryUtility(IIDNormalizer).normalize(self.data.header)
            return u'filter' + name.capitalize()
        return ''

    @property
    def reload_url(self):
        reload_url = '{0}/@@render-portlet?portlethash={1}'.format(
            self.context.absolute_url(),
            self.id
        )
        return reload_url

    @property
    def settings(self):
        return self.data

    @property
    def input_type(self):
        if self.data.input_type == 'links':
            return 'link'
        elif self.data.filter_type == 'single':
            if self.data.input_type == 'checkboxes_radiobuttons':
                return 'radio'
            else:
                return 'dropdown'
        else:
            return 'checkbox'

    def results(self):
        results = get_filter_items(
            target_collection=self.data.target_collection,
            group_by=self.data.group_by,
            filter_type=self.data.filter_type,
            narrow_down=self.data.narrow_down,
            cache_time=self.data.cache_time,
            request_params=self.request.form or {}
        )
        return results


class AddForm(base_AddForm):
    if PLONE5:
        schema = ICollectionFilterPortlet
    else:
        fields = field.Fields(ICollectionFilterPortlet)

    label = _(u"Add Collection Filter Portlet")
    description = _(
        u"This portlet shows grouped criteria of collection results and "
        u"allows filtering of collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base_EditForm):
    if PLONE5:
        schema = ICollectionFilterPortlet
    else:
        fields = field.Fields(ICollectionFilterPortlet)

    label = _(u"Edit Collection Filter Portlet")
    description = _(
        u"This portlet shows grouped criteria of collection results and "
        u"allows filtering of collection results."
    )
