# -*- coding: utf-8 -*-
from plone import api
from plone.tiles.tile import PersistentTile
from plone.app.blocks.layoutbehavior import ILayoutBehaviorAdaptable
from plone.app.blocks.layoutbehavior import ILayoutAware
import re
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from collective.collectionfilter.interfaces import ICollectionish
from collective.collectionfilter.filteritems import CollectionishCollection
from plone.app.contenttypes.behaviors.collection import ICollection


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
        return "ajax_load" not in self.top_request and self.is_available

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


@implementer(ICollectionish)
@adapter(ILayoutBehaviorAdaptable)
class CollectionishLayout(CollectionishCollection):
    """Provide interface for either objects with contentlisting tiles or collections or both"""

    tile = None

    def __init__(self, context):
        self.context = context

        la = ILayoutAware(self.context)
        if la.content:
            urls = re.findall('(@@plone.app.standardtiles.contentlisting/[^"]+)', la.content)
            if urls:
                # TODO: maybe better to get tile data? using ITileDataManager(id)?
                url = context.REQUEST.response.headers.get('x-tile-url')
                tile = self.context.unrestrictedTraverse(urls[0])
                tile.update()
                if context.REQUEST.response.headers.get('x-tile-url'):
                    if url:
                        context.REQUEST.response.headers['x-tile-url'] = url
                    else:
                        del context.REQUEST.response.headers['x-tile-url']

                # print(context.REQUEST.response.headers)
                self.tile = tile
        if self.tile is None:
            # Could still be a ILayoutAware collection
            try:
                self.collection = ICollection(self.context)
            except TypeError:
                raise TypeError("No contentlisting tile or Collection found")
        else:
            self.collection = self.tile  # to get properties

    @property
    def sort_reversed(self):
        if self.tile is not None:
            return self.sort_order == "reverse"
        else:
            return self.collection.sort_reversed

    def results(self, custom_query, request_params):
        """Search results"""
        if self.tile is None:
            return super(CollectionishLayout, self).results(custom_query, request_params)

        builder = getMultiAdapter(
            (self.context, self.context.REQUEST), name="querybuilderresults"
        )

        # Include query parameters from request if not set to ignore
        contentFilter = {}
        if not getattr(self.tile, "ignore_request_params", False):
            contentFilter = dict(self.context.REQUEST.get("contentFilter", {}))

        # TODO: handle events extra params

        return builder(
            query=self.query,
            sort_on=self.sort_on or "getObjPositionInParent",
            sort_order=self.sort_order,
            limit=self.limit,
            batch=False,
            brains=True,
            custom_query=custom_query if custom_query is not None else contentFilter,
        )
