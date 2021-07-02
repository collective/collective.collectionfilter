# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter import PLONE_VERSION
from collective.collectionfilter import utils
from plone.api.portal import get_registry_record as getrec
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform.directives import widget
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

try:
    from plone.formwidget.geolocation.vocabularies import default_map_layer
    from plone.formwidget.geolocation.vocabularies import default_map_layers

    HAS_GEOLOCATION = True
except ImportError:
    HAS_GEOLOCATION = False


def pattern_options():
    options = {
        "basePath": utils.target_collection_base_path,
        "recentlyUsed": True,
        "selectableTypes": utils.target_collection_types,
    }
    if PLONE_VERSION < "5.1":
        del options["basePath"]
        options["selectableTypes"] = [
            "Collection",
        ]
    return options


class ICollectionish(Interface):
    "Adapts object similar to ICollection if has contentlisting tile, or is a collection"


class ICollectionFilterBaseSchema(Interface):

    header = schema.TextLine(
        title=_("label_header", default=u"Filter title"),
        description=_("help_header", u"Title of the rendered filter."),
        required=False,
    )

    target_collection = schema.Choice(
        title=_(u"label_target_collection", default=u"Alternative Target Collection"),
        description=_(
            u"help_target_collection",
            default=u"We use the current context as collection. As an alternative you can select a different "
            u"collection as source for the filter items "
            u"and where the filter is applied.",
        ),
        required=False,
        vocabulary="plone.app.vocabularies.Catalog",
    )
    widget(
        "target_collection", RelatedItemsFieldWidget, pattern_options=pattern_options()
    )

    view_name = schema.TextLine(
        title=_("label_view_name", default=u"Result listing view name"),
        description=_(
            "help_view_name",
            default=u"Optional view name, if the result listing should be"
            u" rendered with a special view. Can be used to direct the request"
            u" to a tile.",
        ),
        required=False,
        default=None,
    )

    content_selector = schema.TextLine(
        title=_("label_content_selector", default=u"Content Selector"),
        description=_(
            "help_content_selector",
            default=u"If your tile or collection has a special class or id for ajax replacement use it here."
            u" Selector will need to work for unthemed view and current page.",
        ),
        required=False,
    )


class ICollectionFilterSchema(ICollectionFilterBaseSchema):
    """Schema for the filter."""

    group_by = schema.Choice(
        title=_("label_groupby", u"Group by"),
        description=_(
            "help_groupby", u"Select the criteria to group the collection results by."
        ),
        required=True,
        vocabulary="collective.collectionfilter.GroupByCriteria",
    )

    show_count = schema.Bool(
        title=_(u"label_show_count", default=u"Show count"),
        description=_(
            u"help_show_count", default=u"Show the result count for each filter group."
        ),
        default=False,
        required=False,
    )

    cache_enabled = schema.Bool(
        title=_(u"label_cache_enabled", default=u"Enable Cache"),
        description=_(
            u"help_cache_enabled",
            default=u"Enable caching of filter items. The cache is cleared as"
            u" soon as the database has any changes.",
        ),
        default=True,
        required=False,
    )

    filter_type = schema.Choice(
        title=_("label_filter_type", u"Filter Type"),
        description=_(
            "help_filter_type",
            u"Select if single or multiple criterias can be selected and if all (and) or any (or) of the selected criterias must be met."  # noqa
            u"Some index types like ``FieldIndex`` (e.g. Type index) only support the any (or) criteria when set to multiple criterias and ignore, if all (and) is set.",  # noqa
        ),
        required=True,
        vocabulary="collective.collectionfilter.FilterType",
    )

    input_type = schema.Choice(
        title=_("label_input_type", u"Input Type"),
        description=_(
            "help_input_type",
            u"Select how the UI of the collection filter should be rendered. "
            u"Wether as links, as checkboxes and radiobuttons or checkboxes and dropdowns.",  # noqa
        ),
        required=True,
        vocabulary="collective.collectionfilter.InputType",
    )

    narrow_down = schema.Bool(
        title=_(u"label_narrow_down", default=u"Narrow down filter options"),  # noqa
        description=_(
            u"help_narrow_down",
            default=u"Narrow down the filter options when a filter of this group is applied."  # noqa
            u" Only options, which are available in the result set will then be displayed."  # noqa
            u" Other filter groups can still narrow down this one, though.",
        ),  # noqa
        default=False,
        required=False,
    )

    hide_if_empty = schema.Bool(
        title=_(u"label_hide_if_empty", default=u"Hide if empty"),  # noqa
        description=_(
            u"help_hide_if_empty",
            default=u"Don't display if there is 1 or no options without selecting a filter yet.",
        ),
        default=False,
        required=False,
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


class ICollectionSearchSchema(ICollectionFilterBaseSchema):
    """Schema for the search filter."""


class ICollectionFilterResultListSort(ICollectionFilterBaseSchema):
    """Schema for the result list sorting."""

    sort_on = schema.Tuple(
        title=_("label_sort_on", u"Enabled sort indexes"),
        description=_("help_sort_on", u"Select the indexes which can be sorted on."),
        value_type=schema.Choice(
            title=u"Index",
            vocabulary="collective.collectionfilter.SortOnIndexes",
        ),
        required=True,
    )
    # NB needed as InAndOut breaks tiles in 5.0
    widget('sort_on', SelectFieldWidget, pattern_options=dict(orderable=True))

    input_type = schema.Choice(
        title=_("label_input_type", u"Input Type"),
        description=_(
            "help_input_type",
            u"Select how the UI of the collection filter should be rendered. "
            u"Wether as links, as checkboxes and radiobuttons or checkboxes and dropdowns.",  # noqa
        ),
        required=True,
        vocabulary="collective.collectionfilter.InputType",
    )


class ICollectionSectionFilterSchema(ICollectionFilterBaseSchema):
    """Schema for the navigation filter."""

    show_count = schema.Bool(
        title=_(u"label_show_count", default=u"Show count"),
        description=_(
            u"help_show_count",
            default=u"Show the result count for each filter group.",
        ),
        default=False,
        required=False,
    )

    cache_enabled = schema.Bool(
        title=_(u"label_cache_enabled", default=u"Enable Cache"),
        description=_(
            u"help_cache_enabled",
            default=u"Enable caching of filter items. The cache is cleared as"
            u" soon as the database has any changes.",
        ),
        default=True,
        required=False,
    )


class IGroupByCriteria(Interface):
    """Interface for the GroupByCriteria utility.

    groupby provides a datastructure like this::

        GROUPBY_CRITERIA = {
            'Subject': {
                'index': 'Subject',      # Index for querying.
                'metadata': 'Subject',   # Metadata name for fast access.
                'display_modifier': _,   # Function for modifying list items
                                         # for display. Gets the item passed
                'css_modifier': None,    # Change css class of filter item
                'index_modifier': None,  # Change index values before querying
                'value_blacklist': None  # Exclude index values from display
                'sort_key_function': None,  # sort key function. defaults to a lower-cased title.  # noqa
            },
        }
    """


class IGroupByModifier(Interface):
    """Adapter interface for modifying the groupby criteria data structure,
    after it has been initially created.
    """


class ICollectionFilterBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


if HAS_GEOLOCATION:

    def map_layer_default():
        return getrec(name="geolocation.default_map_layer", default=default_map_layer)

    def map_layers_default():
        return getrec(name="geolocation.map_layers", default=default_map_layers)

    class ICollectionMapsSchema(ICollectionFilterBaseSchema):
        """schema for maps filtering"""

        narrow_down = schema.Bool(
            title=_(u"label_narrow_down_results", default=u"Narrow down result"),
            description=_(
                u"help_narrow_down_results",
                default=u"Narrow down the result after zooming/moving the map.",
            ),
            default=False,
            required=False,
        )

        default_map_layer = schema.Choice(
            title=_(u"default_map_layer", u"Default map layer"),
            description=_(
                u"help_default_map_layer", default=u"Set the default map layer"
            ),
            required=False,
            defaultFactory=map_layer_default,
            vocabulary="plone.formwidget.geolocation.vocabularies.map_layers",
        )

        map_layers = schema.List(
            title=_(u"label_map_layers", u"Map Layers"),
            description=_(u"help_map_layers", default=u"Set the available map layers"),
            required=False,
            defaultFactory=map_layers_default,
            missing_value=[],
            value_type=schema.Choice(
                vocabulary="plone.formwidget.geolocation.vocabularies.map_layers"
            ),
        )  # noqa: E501
