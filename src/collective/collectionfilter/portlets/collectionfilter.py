from .. import _
from ..filteritems import get_filter_items
from ..interfaces import ICollectionFilterSchema
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
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
    additive_filter = False
    # additive_operator = 'and'
    # list_scaling = None

    def __init__(
        self,
        header=u"",
        target_collection=None,
        group_by=u"",
        show_count=False,
        cache_time=60,
        additive_filter=False,
        # additive_operator='and',
        # list_scaling=None
    ):
        self.header = header
        self.target_collection = target_collection
        self.group_by = group_by
        self.show_count = show_count
        self.cache_time = cache_time
        self.additive_filter = additive_filter
        # self.additive_operator = additive_operator
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

    def header_title(self):
        if self.data.header:
            return self.data.header

        collection = uuidToObject(self.data.target_collection)
        return collection.Title() if collection else None

    def results(self):
        # return cached
        results = get_filter_items(
            self.data.target_collection,
            self.data.group_by,
            self.data.additive_filter,
            self.data.cache_time,
            self.request.form or {})
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
