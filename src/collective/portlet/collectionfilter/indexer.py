from collective.portlet.collectionfilter.vocabularies import EMPTY_MARKER
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer


@indexer(IDexterityContent)
def subject_indexer(obj):
    """Subject indexer. Returns EMPTY_MARKER, if no subjects are set.
    """
    cat = ICategorization(obj, None)
    cats = getattr(cat, 'subjects', None) or (EMPTY_MARKER, )
    cats = tuple([it.encode('utf-8', 'replace') for it in cats])
    return cats
