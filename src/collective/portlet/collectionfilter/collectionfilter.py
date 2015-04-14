from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.portlet.collectionfilter import msgFact as _
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.portlets.browser import z3cformhelper
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.memoize.instance import memoize
from plone.portlet.collection.collection import Renderer as CollectionRenderer
from plone.portlets.interfaces import IPortletDataProvider
from z3c.form import field
from zope import schema
from zope.interface import implements

try:
    from plone.app.event.browser.event_listing import EventListing
    from plone.app.event.base import RET_MODE_OBJECTS
except ImportError:
    class EventListing(object):
        pass


GROUPBY_CRITERIA = {
    'Subject': {
        'index': 'Subject',  # For querying
        'metadata': 'Subject',  # For constructing the list
        'display_modifier': None,  # For modifying list items (e.g. dates)
        'query_range': None  # For range searches (e.g. for dates or numbers)
    },
    'Author': {
        'index': 'Creator',
        'metadata': 'Creator',
        'display_modifier': None,
        'query_range': None
    },
    'Portal Type': {
        'index': 'portal_type',
        'metadata': 'portal_type',
        'display_modifier': None,
        'query_range': None,
    }
}

LIST_SCALING = ['No Scaling', 'Linear', 'Logarithmic']

FACETED_OPERATOR = ['and', 'or']


class ICollectionFilterPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_('label_header', default=u'Portlet header'),
        description=_(
            'help_header'
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

    faceted = schema.Bool(
        title=_(u'label_faceted', default=u'Faceted Filter'),
        description=_(
            u'help_faceted',
            default=u'Use faceted filtering by keeping previously selected '
                    u'criterias active.'),
        default=False,
        required=False
    )

    faceted_operator = schema.Choice(
        title=_(u'label_faceted_operator', default=u'Faceted Filter Operator'),
        description=_(
            u'help_faceted_operator',
            default=u'Select, if all (and) or any (or) selected filter '
                    u'criterias must be met.'),
        required=True,
        vocabulary='collective.portlet.collectionfilter.FacetedOperator',
    )

    show_count = schema.Bool(
        title=_(u'label_show_count', default=u'Show count'),
        description=_(
            u'help_show_count',
            default=u'Show the result count for each filter group.'),
        default=False,
        required=False
    )

    list_scaling = schema.Choice(
        title=_('label_list_scaling', u'List scaling'),
        description=_(
            'help_list_scaling',
            u'Scale list by count. If a scaling is selected, a the list '
            u'appears as tagcloud.'
        ),
        required=True,
        vocabulary='collective.portlet.collectionfilter.ListScaling',
    )


class Assignment(base.Assignment):
    implements(ICollectionFilterPortlet)

    def __init__(
        self,
        header=u"",
        target_collection=None,
        group_by=u"",
        faceted=False,
        faceted_operator='and',
        show_count=False,
        list_scaling=None
    ):
        self.header = header
        self.target_collection = target_collection
        self.group_by = group_by
        self.faceted = faceted
        self.faceted_operator = faceted_operator
        self.show_count = show_count
        self.list_scaling = list_scaling

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u'Collection Filter')


class Renderer(CollectionRenderer):
    render = ViewPageTemplateFile('collectionfilter.pt')

    @property
    def available(self):
        return True

    def header_title(self):
        if self.data.header:
            return self.data.header

        collection = self.collection(self.data.target_collection)
        if collection is None:
            return None
        else:
            return collection.Title()

    @property
    @memoize
    def collection(self):
        item = uuidToObject(self.data.target_collection)
        return item

    def results(self):
        ret = []
        # url_query = self.request.form
        collection = self.collection
        if collection:
            collection_layout = collection.getLayout()
            default_view = collection.restrictedTraverse(collection_layout)
            results = []
            if isinstance(default_view, EventListing):
                # special plone.app.event event_listing handling
                # TODO: that's cumbersome. can't pae event_listing be a
                #       instance of the Collection class?
                results = default_view.events(
                    ret_mode=RET_MODE_OBJECTS,
                    batch=False
                )
            elif getattr(default_view, 'results', False):
                results = default_view.results()
            else:
                results = collection.results()

            grouped_results = {}
            for item in results:
                attr = GROUPBY_CRITERIA[self.data.group_by]['metadata']
                val = getattr(item, attr, None)
                if callable(val):
                    val = val()
                if not getattr(val, '__iter__', False):
                    val = list(val)
                for it in val:
                    grouped_results.setdefault(it, [])
                    grouped_results[it].append(item)
            for subject, items in grouped_results.iteritems():
                ret.append(dict(
                    title=subject,
                    url='{0}/?{1}={2}'.format(
                        self.collection.absolute_url(),
                        GROUPBY_CRITERIA[self.data.group_by]['index'],
                        subject
                    ),
                    count=len(items)
                ))

        return ret


class AddForm(z3cformhelper.AddForm):
    fields = field.Fields(ICollectionFilterPortlet)

    label = _(u"Add Collection Filter Portlet")
    description = _(
        u"This portlet shows grouped criteria of collection results and "
        u"allows filtering of collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(z3cformhelper.EditForm):
    fields = field.Fields(ICollectionFilterPortlet)

    label = _(u"Edit Collection Filter Portlet")
    description = _(
        u"This portlet shows grouped criteria of collection results and "
        u"allows filtering of collection results."
    )
