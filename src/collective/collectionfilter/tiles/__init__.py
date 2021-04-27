# -*- coding: utf-8 -*-
from plone import api
from plone.tiles.tile import PersistentTile


class DictDataWrapper(object):
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError


class BaseFilterTile(PersistentTile):
    def available(self):
        # do not render when page is ajax loaded
        return "ajax_load" not in self.top_request

    @property
    def edit_url(self):
        if not api.user.has_permission("cmf.ModifyPortalContent", obj=self.context):
            return None
        return self.url.replace("@@", "@@edit-tile/")

    @property
    def settings(self):
        return DictDataWrapper(self.data)

    @property
    def filter_id(self):
        return self.id

    @property
    def reload_url(self):
        return self.url
