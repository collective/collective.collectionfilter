# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
from plone.api import env


_ = MessageFactory('collective.collectionfilter')

PLONE_VERSION = env.plone_version()
