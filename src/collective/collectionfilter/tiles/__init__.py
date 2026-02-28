from collective.collectionfilter import _
from collective.collectionfilter.filteritems import CollectionishCollection
from collective.collectionfilter.interfaces import ICollectionish
from plone import api
from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.app.blocks.layoutbehavior import ILayoutBehaviorAdaptable
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.tiles.tile import PersistentTile
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer

import re


# tile names actijg collectionish
COLLECTIONISH_TARGETS = [
    "plone.app.standardtiles.contentlisting",
]


class DictDataWrapper:
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
        if not api.user.has_permission("Modify portal content", obj=self.context):
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
    if not isinstance(spec, list):
        spec = [spec]
    request = getRequest()
    la = ILayoutAware(context)
    layout = (
        la.customContentLayout
        if la.customContentLayout is not None
        else la.contentLayout if la.contentLayout is not None else la.content
    )
    if layout is None:
        return []
    possible_urls = re.findall(r"(@@[\w\.]+/\w+)", layout)
    urls = []
    for name in spec:
        urls += [url for url in possible_urls if url.startswith(f"@@{name}")]
    # TODO: maybe better to get tile data? using ITileDataManager(id)?
    our_tile = request.response.headers.get("x-tile-url")
    tiles = [context.unrestrictedTraverse(str(url)) for url in urls]
    # mosaic get confused if we are doing this while creating a filter tile
    if request.response.headers.get("x-tile-url"):
        if our_tile:
            request.response.headers["x-tile-url"] = our_tile
        else:
            del request.response.headers["x-tile-url"]
    return tiles


@implementer(ICollectionish)
@adapter(ILayoutBehaviorAdaptable)
class CollectionishLayout(CollectionishCollection):
    """Provide interface for either objects with contentlisting tiles or collections or both"""

    tile = None
    collection = None

    def __init__(self, context):
        """Adapt either collections or contentlisting tile. The name is sorted content selector"""
        self.context = context
        self.collection = ICollection(self.context, None)

        if self.collection is None:
            # context might not be adaptable -> try to find a collectionish tile
            self.selectContent()

    def selectContent(self, selector=None):
        """Pick tile that selector will match, otherwise pick first one.
        Return None if no listing tile or collection is suitable, else return this adapter.
        """
        if selector is None:
            selector = ""
        self.tile = None
        tiles = findall_tiles(self.context, COLLECTIONISH_TARGETS)
        for tile in tiles:
            tile.update()
            tile_classes = getattr(tile, "tile_class", "").split() + [""]
            # First tile that matches all the selector classes
            if all([_class in tile_classes for _class in selector.split(".")]):
                self.tile = tile
                break
        if tiles and self.tile is None:
            # TODO: what if the class is inside a special template? Just pick first?
            # none of the selectors worked. Just pick any and hope it works?
            self.tile = tile
        if self.tile is not None:
            # we have to set self.collection always to self.tile to get the
            # correct query
            self.collection = self.tile
            return self
        if self.collection is not None:
            # this context is a Collection ILayoutAware enabled but there were
            # no COLLECTIONISH_TARGETS tiles found. Likely because "layout_view"
            # is not enabled here.
            return self

    @property
    def sort_reversed(self):
        if self.tile is not None:
            return self.sort_order == "reverse"
        return self.collection.sort_reversed

    @property
    def content_selector(self):
        """will return None if no tile or collection found"""
        if self.collection is None:
            return
        if self.tile is None:
            return super().content_selector
        classes = ["contentlisting-tile"]
        if getattr(self.tile, "tile_class", ""):
            classes += self.tile.tile_class.split()
        return "." + ".".join(classes)

    def results(self, custom_query, request_params):
        """Search results"""
        if self.tile is None:
            return super().results(custom_query, request_params)

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
    # TODO: is ok in the acquisition path?
    target = tile.collection
    if target is not None:
        target = queryAdapter(target.getObject(), ICollectionish)
    if target is not None:
        target = target.selectContent("")
    if target is None or target.content_selector is None:
        api.portal.show_message(
            _(
                "You will need to add a Content Listing tile or target a collection to make Filters work"
            ),
            request=tile.context.REQUEST,
            type="warning",
        )
        return False
    return True


def validateFilterMosaicModify(context, event):
    # search the layout for any filters and then see if they have a matching listing
    tiles = findall_tiles(context, "collective.collectionfilter.tiles.")
    for tile in tiles:
        if not validateFilterTileModify(tile, event):
            break
