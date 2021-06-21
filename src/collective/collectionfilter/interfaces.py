# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter import PLONE_VERSION
from collective.collectionfilter import utils
from plone.api.portal import get_registry_record as getrec
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
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


class ICollectionFilterBaseSchema(Interface):

    header = schema.TextLine(
        title=_("label_header", default=u"Filter title"),
        description=_("help_header", u"Title of the rendered filter or leave blank for no header"),
        required=False,
    )

    target_collection = schema.Choice(
        title=_(u"label_target_collection", default=u"Alternative Target"),
        description=_(
            u"help_target_collection",
            default=u"Filter the results of this Page or Collection, or else pick a Page or Collection "
            u"this filter will take you to"
        ),
        required=False,
        vocabulary="plone.app.vocabularies.Catalog",
    )
    directives.widget("target_collection", RelatedItemsFieldWidget, pattern_options=pattern_options())

    content_selector = schema.TextLine(
        title=_("label_content_selector", default=u"Content CSS Selector"),
        description=_(
            "help_content_selector",
            default=u"The part of the page you would like to update if using a alternate target or different theme. "
            u"Only useful if AJAX mode is enabled."
        ),
        required=True,  # TODO: blank should mean it uses default tile or collection selector
        default=u"#content-core",
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


class ICollectionFilterSchema(ICollectionFilterBaseSchema):
    """Schema for the filter."""

    group_by = schema.Choice(
        title=_("label_groupby", u"Filter by"),
        description=_(
            "help_groupby", u"Select the field to filter the listing by."
        ),
        required=True,
        vocabulary="collective.collectionfilter.GroupByCriteria",
    )

    input_type = schema.Choice(
        title=_("label_input_type", u"Input Type"),
        description=_(
            "help_input_type",
            u"How the user will pick filter options"
        ),
        required=True,
        vocabulary="collective.collectionfilter.InputType",
    )

    show_count = schema.Bool(
        title=_(u"label_show_count", default=u"Show count"),
        description=_(
            u"help_show_count", default=u"Show the result count for each filter option (can impact site performance)"
        ),
        default=False,
        required=False,
    )

    filter_type = schema.Choice(
        title=_("label_filter_type", u"Filter Type"),
        description=_(
            "help_filter_type",
            u"A Single filter shows results of on option at a time, OR will add results for each option picked or "
            u"AND to reduce results where only all options match. "
            u"Note some Filters don't support AND so multiple options will increase results."
        ),
        required=True,
        vocabulary="collective.collectionfilter.FilterType",
    )

    # TODO: Narrow down is really a way to do AND using single select? What does OR+narrow down mean?
    narrow_down = schema.Bool(
        title=_(u"label_narrow_down", default=u"Narrow down filter options"),  # noqa
        description=_(
            u"help_narrow_down",
            default=u"Selection will reduce the options shown otherwise show all options."  # noqa
            u" Selection of other filters will reduce options regardless.",
        ),  # noqa
        default=False,
        required=False,
    )

    hide_if_empty = schema.Bool(
        title=_(u"label_hide_if_empty", default=u"Hide if empty"),  # noqa
        description=_(
            u"help_hide_if_empty",
            default=u"Show only if there are options to pick",
        ),
        default=False,
        required=False,
    )

    directives.order_before(header='cache_enabled')
    directives.order_before(target_collection='cache_enabled')
    directives.order_before(content_selector='cache_enabled')
    directives.order_before(view_name='cache_enabled')

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
        title=_("label_sort_on", u"Enabled sort fields"),
        description=_("help_sort_on", u"Select the fields to allow sort on."),
        value_type=schema.Choice(
            title=u"Index",
            vocabulary="collective.collectionfilter.SortOnIndexes",
        ),
        required=True,
    )
    # NB needed as InAndOut breaks tiles in 5.0
    directives.widget('sort_on', SelectFieldWidget, pattern_options=dict(orderable=True))

    input_type = schema.Choice(
        title=_("label_input_type", u"Input Type"),
        description=_(
            "help_input_type",
            u"How the user will pick filter options"
        ),
        required=True,
        vocabulary="collective.collectionfilter.InputType",
    )

    directives.order_before(header='view_name')
    directives.order_before(target_collection='view_name')
    directives.order_before(content_selector='view_name')
    directives.order_after(view_name='input_type')


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
