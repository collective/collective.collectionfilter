# -*- coding: utf-8 -*-
from plone.tiles.tile import Tile
from ..baseviews import BaseFilterView


class FilterTile(BaseFilterView, Tile):
    
    @property
    def id(self):
        return u''

    @property
    def reload_url(self):
        return u''
