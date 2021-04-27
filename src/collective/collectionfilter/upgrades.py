from collective.collectionfilter.portlets.collectionfilter import (  # noqa
    ICollectionFilterPortlet,
)
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import ISetupTool
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
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
                            u"Set {0} input_type to ``checkboxes_radiobuttons``".format(
                                assignment
                            )
                        )  # noqa
                        setattr(assignment, "input_type", "checkboxes_radiobuttons")
                    else:
                        logger.info(
                            u"Set {0} input_type to ``links``".format(assignment)
                        )  # noqa
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
