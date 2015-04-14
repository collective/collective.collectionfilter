from collective.portlet.collectionfilter import msgFact as _
from collective.portlet.collectionfilter.collectionfilter import FACETED_OPERATOR  # noqa
from collective.portlet.collectionfilter.collectionfilter import GROUPBY_CRITERIA  # noqa
from collective.portlet.collectionfilter.collectionfilter import LIST_SCALING
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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
