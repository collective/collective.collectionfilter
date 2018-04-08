# -*- coding: utf-8 -*-
from plone.tiles.tile import Tile
from ..baseviews import BaseFilterView


class SearchTile(BaseFilterView, Tile):
    
    @property
    def id(self):
        return u''

    @property
    def reload_url(self):
        return u''
