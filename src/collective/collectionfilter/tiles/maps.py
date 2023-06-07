from collective.collectionfilter.baseviews import BaseMapsView
from collective.collectionfilter.interfaces import ICollectionMapsSchema
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from zope.interface import implementer


class IMapsTile(Schema, ICollectionMapsSchema):
    """schema for maps tile"""


@implementer(IMapsTile)
class MapsTile(BaseFilterTile, BaseMapsView):
    """Maps View"""
