# -*- coding: utf-8 -*-
from collective.collectionfilter.baseviews import BaseInfoView
from collective.collectionfilter.interfaces import ICollectionFilterInfo  # noqa
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from zope.interface import implementer


class IInfoTile(Schema, ICollectionFilterInfo):
    pass


@implementer(IInfoTile)
class InfoTile(BaseFilterTile, BaseInfoView):
    """ Info Tile """

    # TODO: put in addition field for picking header type
