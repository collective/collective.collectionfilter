from collective.collectionfilter.portlets.collectionfilter import (  # noqa
    ICollectionFilterPortlet,
)
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import ISetupTool
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component.hooks import getSite

import logging


_marker = []

logger = logging.getLogger(__file__)


def upgrade_portlet_input_type(ctx):
    # See: https://docs.plone.org/4/en/old-reference-manuals/portlets/appendix/schema_update.html
    context = getSite()
    cat = getToolByName(context, "portal_catalog")
    query = {"object_provides": ILocalPortletAssignable.__identifier__}
    all_brains = cat(**query)
    all_content = [brain.getObject() for brain in all_brains]
    all_content.append(context)
    for content in all_content:
        for manager_name, manager in getUtilitiesFor(IPortletManager, context=content):
            mapping = getMultiAdapter(
                (content, manager), IPortletAssignmentMapping
            )  # noqa
            for id, assignment in mapping.items():
                if ICollectionFilterPortlet.providedBy(assignment):
                    as_input = getattr(assignment, "as_input")
                    if as_input:
                        logger.info(
                            "Set {} input_type to ``checkboxes_radiobuttons``".format(
                                assignment
                            )
                        )  # noqa
                        setattr(assignment, "input_type", "checkboxes_radiobuttons")
                    else:
                        logger.info(f"Set {assignment} input_type to ``links``")  # noqa
                        setattr(assignment, "input_type", "links")


def loadMigrationProfile(context, profile, steps=_marker):
    if not ISetupTool.providedBy(context):
        context = getToolByName(context, "portal_setup")
    if steps is _marker:
        context.runAllImportStepsFromProfile(profile, purge_old=False)
    else:
        for step in steps:
            context.runImportStepFromProfile(
                profile, step, run_dependencies=False, purge_old=False
            )


def reapply_profile(context):
    loadMigrationProfile(
        context,
        "profile-collective.collectionfilter:default",
    )


def upgrade_to_plone6(context):
    # Delete deprecated keys in the registry
    keys_to_delete = [
        "plone.bundles/collectionfilter-bundle.compile",
        "plone.bundles/collectionfilter-bundle.develop_css",
        "plone.bundles/collectionfilter-bundle.develop_javascript",
        "plone.bundles/collectionfilter-bundle.last_compilation",
        "plone.bundles/collectionfilter-bundle.merge_with",
        "plone.bundles/collectionfilter-bundle.resources",
        "plone.bundles/collectionfilter-bundle.stub_js_modules",
        "plone.resources/collectionfilter-bundle.conf",
        "plone.resources/collectionfilter-bundle.css",
        "plone.resources/collectionfilter-bundle.deps",
        "plone.resources/collectionfilter-bundle.export",
        "plone.resources/collectionfilter-bundle.init",
        "plone.resources/collectionfilter-bundle.js",
        "plone.resources/collectionfilter-bundle.url",
        "plone.resources/collectionfilter.conf",
        "plone.resources/collectionfilter.css",
        "plone.resources/collectionfilter.deps",
        "plone.resources/collectionfilter.export",
        "plone.resources/collectionfilter.init",
        "plone.resources/collectionfilter.js",
        "plone.resources/collectionfilter.url",
    ]
    registry = getUtility(IRegistry)
    for key in keys_to_delete:
        if key in registry.records.keys():
            del registry.records[key]

    reapply_profile(context)
