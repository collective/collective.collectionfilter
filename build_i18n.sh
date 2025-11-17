#!/bin/sh
I18NDUDE=i18ndude
I18NPATH=./src/collective/collectionfilter
DOMAIN=collective.collectionfilter
PLONE_DOMAIN=plone

# For collective.collectionfilter.pot file
$I18NDUDE rebuild-pot --pot $I18NPATH/locales/$DOMAIN.pot --create $DOMAIN $I18NPATH
$I18NDUDE sync --pot $I18NPATH/locales/$DOMAIN.pot $I18NPATH/locales/*/LC_MESSAGES/$DOMAIN.po

# For plone.pot file
$I18NDUDE rebuild-pot --pot $I18NPATH/locales/$PLONE_DOMAIN.pot --create $PLONE_DOMAIN $I18NPATH/portlets/profiles/portlets_with_maps/ $I18NPATH/portlets/profiles/default/
$I18NDUDE sync --pot $I18NPATH/locales/$PLONE_DOMAIN.pot $I18NPATH/locales/*/LC_MESSAGES/$PLONE_DOMAIN.po
