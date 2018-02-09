# -*- coding: utf-8 -*-
from . import _
from . import utils
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform.directives import widget
from zope import schema
from zope.interface import Interface


class ICollectionFilterSchema(Interface):

    target_collection = schema.Choice(
        title=_(u'label_target_collection', default=u'Target Collection'),
        description=_(
            u'help_target_collection',
            default=u'The collection, which is the source for the filter '
                    u'items and where the filter is applied.'
        ),
        required=True,
        vocabulary='plone.app.vocabularies.Catalog',
    )
    widget(
        'target_collection',
        RelatedItemsFieldWidget,
        pattern_options={
            'basePath': utils.target_collection_base_path,
            'recentlyUsed': True,
            'selectableTypes': ['Collection'],
        }
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

    filter_type = schema.Choice(
        title=_('label_filter_type', u'Filter Type'),
        description=_(
            'help_filter_type',
            u'Select if single or multiple criterias can be selected and if all (and) or any (or) of the selected criterias must be met.'   # noqa
            u'Some index types like ``FieldIndex`` (e.g. Type index) only support the any (or) criteria when set to multiple criterias and ignore, if all (and) is set.'  # noqa
        ),
        required=True,
        vocabulary='collective.collectionfilter.FilterType',
    )

    input_type = schema.Choice(
        title=_('label_input_type', u'Input Type'),
        description=_(
            'help_input_type',
            u'Select how the UI of the collection filter should be rendered. '
            u'Wether as links, as checkboxes and radiobuttons or checkboxes and dropdowns.'  # noqa
        ),
        required=True,
        vocabulary='collective.collectionfilter.InputType',
    )

    narrow_down = schema.Bool(
        title=_(u'label_narrow_down', default=u'Narrow down filter options'),  # noqa
        description=_(
            u'help_narrow_down',
            default=u'Narrow down the filter options when a filter of this group is applied.'  # noqa
                    u' Only options, which are available in the result set will then be displayed.'  # noqa
                    u' Other filter groups can still narrow down this one, though.'),  # noqa
        default=False,
        required=False
    )

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
        vocabulary='plone.app.vocabularies.Catalog',
    )
    widget(
        'target_collection',
        RelatedItemsFieldWidget,
        pattern_options={
            'basePath': utils.target_collection_base_path,
            'recentlyUsed': True,
            'selectableTypes': ['Collection'],
        }
    )


class IGroupByCriteria(Interface):
    """Interface for the GroupByCriteria utility.

    groupby provides a datastructure like this::

        GROUPBY_CRITERIA = {
            'Subject': {
                'index': 'Subject',     # Index for querying.
                'metadata': 'Subject',  # Metadata name for fast access.
                'display_modifier': _,  # Function for modifying list items
                                        # for display. Gets the item passed
            },
        }
    """


class IGroupByModifier(Interface):
    """Adapter interface for modifying the groupby criteria data structure,
    after it has been initially created.
    """
