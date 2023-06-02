from collective.collectionfilter.baseviews import BaseMapsView
from collective.collectionfilter.interfaces import ICollectionMapsSchema
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.utils import get_top_request
from zope.interface import implementer


class IMapsTile(Schema, ICollectionMapsSchema):
    """schema for maps tile"""


@implementer(IMapsTile)
class MapsTile(BaseFilterTile, BaseMapsView):
    """Maps View"""
