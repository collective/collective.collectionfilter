from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.vocabularies.catalog import CatalogSource
from zope import schema
from zope.interface import Interface

from . import _


class ICollectionFilterSchema(Interface):

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
        vocabulary='collective.collectionfilter.GroupByCriteria',
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
            default=u'Use additive_filter filtering by keeping previously selected criterias active.'),  # noqa
        default=False,
        required=False
    )

#    filter_operator = schema.Choice(
#        title=_(
#           u'label_filter_operator', default=u'Filter Operator'),
#        description=_(
#            u'help_filter_operator',
#            default=u'Select, if all (and) or any (or) of the selected filter criterias must be met.'),  # noqa
#        default='and',
#        required=False,
#        vocabulary='collective.collectionfilter.AdditiveOperator',
#    )

#    list_scaling = schema.Choice(
#        title=_('label_list_scaling', u'List scaling'),
#        description=_(
#            'help_list_scaling',
#            u'Scale list by count. If a scaling is selected, a the list '
#            u'appears as tagcloud.'
#        ),
#        required=True,
#        vocabulary='collective.collectionfilter.ListScaling',
#    )


class ICollectionSearchSchema(Interface):

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


class IGroupByCriteria(Interface):
    """Interface for creating the GroupByCriteria data structure.

    For example::

        GROUPBY_CRITERIA = {
            'Subject': {
                'index': 'Subject',     # Index for querying.
                'metadata': 'Subject',  # Metadata name for fast access.
                'display_modifier': _,  # Function for modifying list items
                                        # for display. Gets the item passed.
            },
        }

    """
