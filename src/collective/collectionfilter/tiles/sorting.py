# -*- coding: utf-8 -*-
from collective.collectionfilter.baseviews import BaseSortOnView
from collective.collectionfilter.interfaces import (  # noqa
    ICollectionFilterResultListSort,
)
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from zope.interface import implementer


class ISortOnTile(Schema, ICollectionFilterResultListSort):
    pass


@implementer(ISortOnTile)
class SortOnTile(BaseFilterTile, BaseSortOnView):
    """ Sorting Tile """
