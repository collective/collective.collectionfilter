# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.interfaces import IGroupByModifier
from collective.collectionfilter.utils import safe_encode
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.app.vocabularies.types import (  # noqa: E501
    ReallyUserFriendlyTypesVocabularyFactory,
)
from plone.registry.interfaces import IRegistry
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import plone.api
import six


# Use this EMPTY_MARKER for your custom indexer to index empty criterions.
EMPTY_MARKER = "__EMPTY__"
TEXT_IDX = "SearchableText"
GEOLOC_IDX = [
    "latitude",
    "longitude",
]
GROUPBY_BLACKLIST = [
    "CreationDate",
    "Date",
    "Description",
    "EffectiveDate",
    "ExpirationDate",
    "ModificationDate",
    "Title",
    "UID",
    "cmf_uid",
    "created",
    "effective",
    "end",
    "expires",
    "getIcon",
    "getId",
    "getObjSize",
    "getRemoteUrl",
    "id",
    "last_comment_date",
    "listCreators",
    "meta_type",
    "modified",
    "start",
    "sync_uid",
    "total_comments",
] + GEOLOC_IDX  # latitude/longitude is handled as a range filter ... see query.py  # noqa
DEFAULT_FILTER_TYPE = "single"
LIST_SCALING = ["No Scaling", "Linear", "Logarithmic"]


def translate_value(value, *args, **kwargs):
    return translate(_(value), context=getRequest())


def translate_messagefactory(value, *args, **kwargs):
    return translate(value, context=getRequest())


def make_bool(value):
    """Transform into a boolean value."""
    truthy = [
        safe_encode("true"),
        safe_encode("1"),
        safe_encode("t"),
        safe_encode("yes"),
    ]
    if value is None:
        return
    if isinstance(value, bool):
        return value
    value = safe_encode(value)
    value = value.lower()
    if value in truthy:
        return True
    else:
        return False


def yes_no(value):
    """Return i18n message for a value."""
    if value:
        return _(u"Yes")
    else:
        return _(u"No")


def get_yes_no_title(item, *args, **kwargs):
    """Return a readable representation of a boolean value."""
    value = yes_no(item)
    return translate_messagefactory(value)


def translate_portal_type(value, *args, **kwargs):
    vocabulary = ReallyUserFriendlyTypesVocabularyFactory(None)
    term = vocabulary.getTermByToken(value)
    return term.title if term else value


def selected_path_children(path, query):
    """ We only want the ancestors and direct child folders of current selections to be options.
        This means we don't get overloaded with full tree of options. If no query then assume
        portal is the query so return top level folders.
     """
    # Get path, remove portal root from path, remove leading /
    portal = plone.api.portal.get()
    portal_parts = portal.getPhysicalPath()
    portal_path = "/".join(list(portal_parts))
    if not query:
        filters = ['']
    else:
        filters = query  # TODO: process it
    for filter in filters:
        if not path.startswith('/'.join([portal_path, filter])):
            continue
        parts = path.split("/")
        selected_parts = filter.split("/") if filter else []
        sub_parts = parts[len(portal_parts): -1]  # We only want parents
        sub_parts = sub_parts[:len(selected_parts) + 1]  # Only want direct descendents of whats been picked
        if not sub_parts:
            continue
        for i in range(1, len(sub_parts) + 1):
            yield "/".join(sub_parts[:i])


def path_to_title(path, idx, filter_type):
    portal = plone.api.portal.get()
    # ctype = "folder"
    path = "/".join(["/".join(portal.getPhysicalPath()), path])
    container = portal.portal_catalog.searchResults({"path": {"query": path}, "depth": 0})
    if len(container) > 0:
        title = container[0].Title
        # ctype = container[0].portal_type.lower()
    else:
        title = path.split("/")[-1]
    if filter_type != "links":
        # so dropdowns look indented
        title = u" " * (len(path.split("/")) - 1) + title
    return title


def path_indent(path):
    level = len(path.split("/"))
    css_class = u"pathLevel{level}".format(level=level)
    return css_class


def relative_to_absolute_path(path):
    # Ensure query string only needs relative path. Internal search needs full path
    return '/'.join(list(plone.api.portal.get().getPhysicalPath()) + path.split("/"))


@implementer(IGroupByCriteria)
class GroupByCriteria:
    """Global utility for retrieving and manipulating groupby criterias.

    1) Populate ``groupby`` catalog metadata.
    2) Do not use blacklisted metadata columns.
    3) Use IGroupByModifier adapters to modify the datastructure.

    """

    _groupby = None
    groupby_modify = {}

    @property
    def groupby(self):

        if self._groupby is not None:
            # The groupby criteria are used at each IBeforeTraverseEvent - so
            # on each request. This has to be fast, so exit early.
            return self._groupby
        self._groupby = {}

        cat = plone.api.portal.get_tool("portal_catalog")
        # get catalog metadata schema, but filter out items which cannot be
        # used for grouping
        metadata = [it for it in cat.schema() if it not in GROUPBY_BLACKLIST] + ['getPath']

        for it in metadata:
            index_modifier = None
            display_modifier = translate_value  # Allow to translate in this package domain per default.  # noqa
            groupby_modifier = None
            sort_key_function = lambda it: it["title"].lower() # noqa
            css_modifier = None
            index_name = dict(getPath="path").get(it, it)
            idx = cat._catalog.indexes.get(index_name)
            index_type = getattr(idx, "meta_type", None)
            if six.PY2 and index_type == "KeywordIndex":
                # in Py2 KeywordIndex accepts only utf-8 encoded values.
                index_modifier = safe_encode
            elif index_type == "BooleanIndex":
                index_modifier = make_bool
                display_modifier = get_yes_no_title
            elif index_type == "ExtendedPathIndex":
                display_modifier = path_to_title
                css_modifier = path_indent
                groupby_modifier = selected_path_children
                index_modifier = relative_to_absolute_path
                sort_key_function = lambda it: it["url"]  # noqa # TODO: should use orderinparent index

            # for portal_type or Type we have some special sauce as we need to translate via fti.i18n_domain.  # noqa
            if it == "portal_type":
                display_modifier = translate_portal_type
            elif it == "Type":
                display_modifier = translate_messagefactory

            self._groupby[it] = {
                "index": index_name,
                "metadata": it,
                "display_modifier": display_modifier,
                "css_modifier": css_modifier,
                "index_modifier": index_modifier,
                "groupby_modifier": groupby_modifier,
                "value_blacklist": None,
                "sort_key_function": sort_key_function,  # sort key function. defaults to a lower-cased title.  # noqa
            }

        modifiers = getAdapters((self,), IGroupByModifier)
        for name, modifier in sorted(modifiers, key=lambda it: it[0]):
            modifier()

        return self._groupby

    @groupby.setter
    def groupby(self, value):
        self._groupby = value


@provider(IVocabularyFactory)
def GroupByCriteriaVocabulary(context):
    """Collection filter group by criteria."""
    groupby = getUtility(IGroupByCriteria).groupby
    items = [SimpleTerm(title=_(it), value=it) for it in groupby.keys()]
    return SimpleVocabulary(items)


# TODO: this should depend on the index type, or be validated against it
@provider(IVocabularyFactory)
def FilterTypeVocabulary(context):
    items = [
        SimpleTerm(title=_("filtertype_single"), value="single"),
        SimpleTerm(title=_("filtertype_and"), value="and"),
        SimpleTerm(title=_("filtertype_or"), value="or"),
    ]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def InputTypeVocabulary(context):
    items = [
        SimpleTerm(title=_("inputtype_links"), value="links"),
        SimpleTerm(
            title=_("inputtype_checkboxes_radiobuttons"),
            value="checkboxes_radiobuttons",
        ),  # noqa
        SimpleTerm(
            title=_("inputtype_checkboxes_dropdowns"), value="checkboxes_dropdowns"
        ),  # noqa
    ]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def ListScalingVocabulary(context):
    items = [SimpleTerm(title=_(it), value=it) for it in LIST_SCALING]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def SortOnIndexesVocabulary(context):
    # we reuse p.a.querystring registry reader for sortable_indexes
    registry = getUtility(IRegistry)
    reader = getMultiAdapter((registry, getRequest()), IQuerystringRegistryReader)
    sortable_indexes = reader().get("sortable_indexes")
    items = [
        SimpleTerm(title=_(v["title"]), value=k) for k, v in sortable_indexes.items()
    ]  # noqa
    return SimpleVocabulary(items)
