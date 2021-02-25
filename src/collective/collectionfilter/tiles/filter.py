# -*- coding: utf-8 -*-
from collective.collectionfilter.baseviews import BaseFilterView
from collective.collectionfilter.interfaces import ICollectionFilterSchema
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from zope.interface import implementer


class IFilterTile(Schema, ICollectionFilterSchema):
    pass


@implementer(IFilterTile)
class FilterTile(BaseFilterTile, BaseFilterView):
    """ Filter Tile """
