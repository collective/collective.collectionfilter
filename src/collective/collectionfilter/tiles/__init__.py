# -*- coding: utf-8 -*-
from plone import api
from plone.tiles.tile import PersistentTile
from plone.app.blocks.layoutbehavior import ILayoutBehaviorAdaptable
from plone.app.blocks.layoutbehavior import ILayoutAware
import re
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.interface import implementer
from collective.collectionfilter import _
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


def findall_tiles(context, spec):
    request = context.REQUEST
    la = ILayoutAware(context)
    layout = la.customContentLayout if la.customContentLayout is not None else la.contentLayout if la.contentLayout is not None else la.content
    if layout is None:
        return []
    urls = re.findall(r'(@@[\w\.]+/\w+)', layout)
    urls = [url for url in urls if url.startswith("@@{}".format(spec))]
    # TODO: maybe better to get tile data? using ITileDataManager(id)?
    our_tile = request.response.headers.get('x-tile-url')
    tiles = [context.unrestrictedTraverse(str(url)) for url in urls]
    # mosaic get confused if we are doing this while creating a filter tile
    if request.response.headers.get('x-tile-url'):
        if our_tile:
            request.response.headers['x-tile-url'] = our_tile
        else:
            del request.response.headers['x-tile-url']
    return tiles


@implementer(ICollectionish)
@adapter(ILayoutBehaviorAdaptable)
class CollectionishLayout(CollectionishCollection):
    """Provide interface for either objects with contentlisting tiles or collections or both"""

    tile = None
    collection = None

    def __init__(self, context):
        """ Adapt either collections or contentlisting tile. The name is sorted content selector """
        self.context = context

        self.selectContent("")  # get first tile

        if self.tile is None:
            # Could still be a ILayoutAware collection
            try:
                self.collection = ICollection(self.context)
            except TypeError:
                self.collection = None
        else:
            self.collection = self.tile  # to get properties

    def selectContent(self, selector=None):
        """ Pick tile that selector will match, otherwise pick first one.
        Return None if no listing tile or collection is suitable, else return this adapter.
         """

        if selector is None:
            selector = ""
        self.tile = None
        tiles = findall_tiles(self.context, "plone.app.standardtiles.contentlisting")
        for tile in tiles:
            tile.update()
            tile_classes = tile.tile_class.split() + ['']
            # First tile that matches all the selector classes
            if all([_class in tile_classes for _class in selector.split(".")]):
                self.tile = tile
                break
        if tiles and self.tile is None:
            # TODO: what if the class is inside a special template? Just pick first?
            # none of the selectors worked. Just pick any and hope it works?
            self.tile = tile
        if self.tile is not None or self.collection is not None:
            return self
        else:
            return None

    @property
    def sort_reversed(self):
        if self.tile is not None:
            return self.sort_order == "reverse"
        else:
            return self.collection.sort_reversed

    @property
    def content_selector(self):
        """ will return None if no tile or colleciton found """
        if self.collection is None:
            return None
        elif self.tile is None:
            return super(CollectionishLayout, self).content_selector
        classes = ["contentlisting-tile"]
        if self.tile.tile_class:
            classes += self.tile.tile_class.split()
        return "." + ".".join(classes)

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


def validateFilterTileModify(tile, event):
    # TODO: is ok in the acquisiton path?
    target = tile.collection
    if target is not None:
        target = queryAdapter(target.getObject(), ICollectionish)
    if target is None or target.content_selector is None:
        api.portal.show_message(
            _(u"You will need to add a Content Listing tile or target a collection to make Filters work"),
            request=tile.context.REQUEST,
            type=u'warning',
        )
        return False
    return True


def validateFilterMosaicModify(context, event):
    # search the layout for any filters and then see if they have a matching listing
    tiles = findall_tiles(context, "collective.collectionfilter.tiles.")
    for tile in tiles:
        if not validateFilterTileModify(tile, event):
            break
