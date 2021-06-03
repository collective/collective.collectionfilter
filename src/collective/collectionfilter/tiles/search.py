# -*- coding: utf-8 -*-
from collective.collectionfilter.baseviews import BaseSearchView
from collective.collectionfilter.interfaces import ICollectionSearchSchema
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from zope.interface import implementer


class ISearchTile(Schema, ICollectionSearchSchema):
    pass


@implementer(ISearchTile)
class SearchTile(BaseFilterTile, BaseSearchView):
    """ Search Tile """
