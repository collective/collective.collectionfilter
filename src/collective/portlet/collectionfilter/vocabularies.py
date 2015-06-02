from collective.portlet.collectionfilter import msgFact as _
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


# Use this EMPTY_MARKER for your custom indexer to index empty criterions.
EMPTY_MARKER = '__EMPTY__'

TEXT_IDX = "SearchableText"

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


@provider(IVocabularyFactory)
def FacetedOperator(context):
    items = [
        SimpleTerm(title=_(it), value=it) for it in FACETED_OPERATOR
    ]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def GroupByCriteria(context):
    """Collection filter group by criteria.
    """
    items = [
        SimpleTerm(title=_(it), value=it) for it in GROUPBY_CRITERIA.keys()
    ]
    return SimpleVocabulary(items)


@provider(IVocabularyFactory)
def ListScaling(context):
    items = [
        SimpleTerm(title=_(it), value=it) for it in LIST_SCALING
    ]
    return SimpleVocabulary(items)
