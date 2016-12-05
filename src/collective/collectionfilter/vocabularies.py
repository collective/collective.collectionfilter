from . import _
from .interfaces import IGroupByCriteria
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


LIST_SCALING = ['No Scaling', 'Linear', 'Logarithmic']
ADDITIVE_OPERATOR = ['and', 'or']


_GroupByCriteria = None


@implementer(IGroupByCriteria)
def GroupByCriteria():
    # This is called for each IBeforeTraverseEvent - so on each request.
    # Cache until restart.
    global _GroupByCriteria
    if _GroupByCriteria:
        return _GroupByCriteria

    cat = plone.api.portal.get_tool('portal_catalog')
    # get catalog metadata schema, but filter out items which cannot be used
    # for grouping
    metadata = filter(lambda it: it not in GROUPBY_BLACKLIST, cat.schema())

    default_group_by = {
        _(it): {
            'index': it,
            'metadata': it,
            'display_modifier': _  # Allow to translate in this package domain per default.  # noqa
        }
        for it in metadata
    }
    _GroupByCriteria = default_group_by
    return _GroupByCriteria


@provider(IVocabularyFactory)
def GroupByCriteriaVocabulary(context):
    """Collection filter group by criteria.
    """
    groupby = getUtility(IGroupByCriteria)()
    items = [SimpleTerm(title=_(it), value=it) for it in groupby.keys()]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def AdditiveOperatorVocabulary(context):
    items = [SimpleTerm(title=_(it), value=it) for it in ADDITIVE_OPERATOR]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def ListScalingVocabulary(context):
    items = [SimpleTerm(title=_(it), value=it) for it in LIST_SCALING]
    return SimpleVocabulary(items)
