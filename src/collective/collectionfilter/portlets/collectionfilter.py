from . import msgFact as _
from .utils import safe_decode
from .utils import safe_encode
from .vocabularies import EMPTY_MARKER
from .vocabularies import GROUPBY_CRITERIA
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.event.base import _prepare_range
from plone.app.event.base import guess_date_from
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import start_end_query
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.memoize import ram
from plone.memoize.volatile import DontCache
from plone.portlets.interfaces import IPortletDataProvider
from time import time
from urllib import urlencode
from zope import schema
from zope.interface import implements

try:
    from plone.app.event.browser.event_listing import EventListing
except ImportError:
    class EventListing(object):
        pass

PLONE5 = getFSVersionTuple()[0] >= 5

if PLONE5:
    base_AddForm = base.AddForm
    base_EditForm = base.EditForm
else:
    from plone.app.portlets.browser.z3cformhelper import AddForm as base_AddForm  # noqa
    from plone.app.portlets.browser.z3cformhelper import EditForm as base_EditForm  # noqa
    from z3c.form import field


class ICollectionFilterPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_('label_header', default=u'Portlet header'),
        description=_(
            'help_header',
            u'Title of the rendered portlet.'
        ),
        required=False,
    )

    target_collection = schema.Choice(
        title=_(u'label_target_collection', default=u'Target Collection'),
        description=_(
            u'help_target_collection',
            default=u'The collection, which is the source for the filter '
                    u'items and where the filter is applied.'
        ),
        required=True,
        source=CatalogSource(
            object_provides=ISyndicatableCollection.__identifier__
        ),
    )

    group_by = schema.Choice(
        title=_('label_groupby', u'Group by'),
        description=_(
            'help_groupby',
            u'Select the criteria to group the collection results by.'
        ),
        required=True,
        vocabulary='collective.portlet.collectionfilter.GroupByCriteria',
    )

    show_count = schema.Bool(
        title=_(u'label_show_count', default=u'Show count'),
        description=_(
            u'help_show_count',
            default=u'Show the result count for each filter group.'),
        default=False,
        required=False
    )

    cache_time = schema.TextLine(
        title=_(u"label_cache_time", default=u"Cache Time (s)"),
        description=_(
            u'help_cache_time',
            default=u"Cache time in seconds. 0 for no caching."
        ),
        default=u'60',
        required=False,
    )

    additive_filter = schema.Bool(
        title=_(u'label_additive_filter', default=u'Additive Filter'),
        description=_(
            u'help_additive_filter',
            default=u'Use additive_filter filtering by keeping previously selected '
                    u'criterias active.'),
        default=False,
        required=False
    )

#    additive_operator = schema.Choice(
#        title=_(
#           u'label_additive_operator', default=u'Additive Filter Operator'),
#        description=_(
#            u'help_additive_operator',
#            default=u'Select, if all (and) or any (or) selected filter '
#                    u'criterias must be met.'),
#        required=True,
#        vocabulary='collective.portlet.collectionfilter.AdditiveOperator',
#    )

#    list_scaling = schema.Choice(
#        title=_('label_list_scaling', u'List scaling'),
#        description=_(
#            'help_list_scaling',
#            u'Scale list by count. If a scaling is selected, a the list '
#            u'appears as tagcloud.'
#        ),
#        required=True,
#        vocabulary='collective.portlet.collectionfilter.ListScaling',
#    )


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

        collection = self.collection
        if collection is None:
            return None
        else:
            return collection.Title()

    @property
    def collection(self):
        item = uuidToObject(self.data.target_collection)
        return item

    def results(self):
        # return cached
        results = get_filter_items(self.collection, self.request.form or {})
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
