# -*- coding: utf-8 -*-
from . import _
from .interfaces import IGroupByCriteria
from .interfaces import IGroupByModifier
from zope.component import getAdapters
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import plone.api

# Use this EMPTY_MARKER for your custom indexer to index empty criterions.
EMPTY_MARKER = '__EMPTY__'
TEXT_IDX = "SearchableText"
GROUPBY_BLACKLIST = [
    'CreationDate',
    'Date',
    'Description',
    'EffectiveDate',
    'ExpirationDate',
    'ModificationDate',
    'Title',
    'UID',
    'cmf_uid',
    'created',
    'effective',
    'end',
    'expires',
    'getIcon',
    'getId',
    'getObjSize',
    'getRemoteUrl',
    'id',
    'last_comment_date',
    'listCreators',
    'meta_type',
    'modified',
    'start',
    'sync_uid',
    'total_comments',
]
DEFAULT_FILTER_TYPE = 'single'
LIST_SCALING = ['No Scaling', 'Linear', 'Logarithmic']


@implementer(IGroupByCriteria)
class GroupByCriteria():
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

        cat = plone.api.portal.get_tool('portal_catalog')
        # get catalog metadata schema, but filter out items which cannot be
        # used for grouping
        metadata = filter(lambda it: it not in GROUPBY_BLACKLIST, cat.schema())

        self._groupby = {
            it: {
                'index': it,
                'metadata': it,
                'display_modifier': _  # Allow to translate in this package domain per default.  # noqa
            }
            for it in metadata
        }

        modifiers = getAdapters((self, ), IGroupByModifier)
        for name, modifier in sorted(modifiers, key=lambda it: it[0]):
            modifier()

        return self._groupby

    @groupby.setter
    def groupby(self, value):
        self._groupby = value


@provider(IVocabularyFactory)
def GroupByCriteriaVocabulary(context):
    """Collection filter group by criteria.
    """
    groupby = getUtility(IGroupByCriteria).groupby
    items = [SimpleTerm(title=_(it), value=it) for it in groupby.keys()]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def FilterTypeVocabulary(context):
    items = [
        SimpleTerm(title=_('filtertype_single'), value='single'),
        SimpleTerm(title=_('filtertype_and'), value='and'),
        SimpleTerm(title=_('filtertype_or'), value='or')
    ]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def InputTypeVocabulary(context):
    items = [
        SimpleTerm(title=_('inputtype_links'), value='links'),
        SimpleTerm(title=_('inputtype_checkboxes_radiobuttons'), value='checkboxes_radiobuttons'),  # noqa
        SimpleTerm(title=_('inputtype_checkboxes_dropdowns'), value='checkboxes_dropdowns')  # noqa
    ]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def ListScalingVocabulary(context):
    items = [SimpleTerm(title=_(it), value=it) for it in LIST_SCALING]
    return SimpleVocabulary(items)
