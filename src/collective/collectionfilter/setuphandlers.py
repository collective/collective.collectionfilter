from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation."""
        return [
            "collective.collectionfilter:uninstall",
            "collective.collectionfilter.tiles:uninstall",
            "collective.collectionfilter.portlets:uninstall",
        ]
