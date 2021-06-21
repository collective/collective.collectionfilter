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
        metadata = [it for it in cat.schema() if it not in GROUPBY_BLACKLIST]

        for it in metadata:
            index_modifier = None
            display_modifier = translate_value  # Allow to translate in this package domain per default.  # noqa
            idx = cat._catalog.indexes.get(it)
            if six.PY2 and getattr(idx, "meta_type", None) == "KeywordIndex":
                # in Py2 KeywordIndex accepts only utf-8 encoded values.
                index_modifier = safe_encode

            if getattr(idx, "meta_type", None) == "BooleanIndex":
                index_modifier = make_bool
                display_modifier = get_yes_no_title

            # for portal_type or Type we have some special sauce as we need to translate via fti.i18n_domain.  # noqa
            if it == "portal_type":
                display_modifier = translate_portal_type
            elif it == "Type":
                display_modifier = translate_messagefactory

            self._groupby[it] = {
                "index": it,
                "metadata": it,
                "display_modifier": display_modifier,
                "css_modifier": None,
                "index_modifier": index_modifier,
                "value_blacklist": None,
                "sort_key_function": lambda it: it[
                    "title"
                ].lower(),  # sort key function. defaults to a lower-cased title.  # noqa
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
        SimpleTerm(title=_("filtertype_single", u"One Option at a time"), value="single"),
        SimpleTerm(title=_("filtertype_and", u"Reduce Results (AND)"), value="and"),
        SimpleTerm(title=_("filtertype_or", u"Expand Results (OR)"), value="or"),
    ]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def InputTypeVocabulary(context):
    items = [
        SimpleTerm(title=_("inputtype_links", u"Links"), value="links"),
        SimpleTerm(
            title=_("inputtype_checkboxes_radiobuttons", u"Radio Buttons (or Checkboxes)"),
            value="checkboxes_radiobuttons",
        ),  # noqa
        SimpleTerm(
            title=_("inputtype_checkboxes_dropdowns", u"Dropdown Menu (or Checkboxes)"), value="checkboxes_dropdowns"
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
