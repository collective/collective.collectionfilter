from collective.collectionfilter.baseviews import BaseResetFilterView
from collective.collectionfilter.interfaces import ICollectionResetFilterSchema
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from zope.interface import implementer


class IResetFilterTile(Schema, ICollectionResetFilterSchema):
    pass


@implementer(IResetFilterTile)
class ResetFilterTile(BaseFilterTile, BaseResetFilterView):
    """Reset Filter Tile"""
