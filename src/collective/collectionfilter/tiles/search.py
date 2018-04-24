# -*- coding: utf-8 -*-
from . import DictDataWrapper
from ..baseviews import BaseFilterView
from ..interfaces import ICollectionSearchSchema
from plone.supermodel.model import Schema
from plone.tiles.tile import PersistentTile
from zope.interface import implementer


class ISearchTile(Schema, ICollectionSearchSchema):
    pass


@implementer(ISearchTile)
class SearchTile(BaseFilterView, PersistentTile):

    @property
    def settings(self):
        return DictDataWrapper(self.data)

    @property
    def filter_id(self):
        return self.id

    @property
    def reload_url(self):
        return u''
