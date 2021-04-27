# -*- coding: utf-8 -*-
from plone.api import env
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("collective.collectionfilter")

PLONE_VERSION = env.plone_version()
