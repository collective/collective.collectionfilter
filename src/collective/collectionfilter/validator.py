# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_chain
from collective.collectionfilter import _
from collective.collectionfilter.filteritems import ICollectionish
from collective.collectionfilter.interfaces import ICollectionFilterBaseSchema
from collective.collectionfilter.interfaces import ICollectionFilterBrowserLayer
from plone.dexterity.interfaces import IDexterityContent
from z3c.form import validator
from z3c.form.interfaces import IValidator
from zope.component import adapter
from zope.component import queryAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
from zope.schema.interfaces import IField
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.portlets.interfaces import IPortletAssignmentMapping


# Portlets can always validate.
# Tiles can validate if its a collection, otherwise rely on status message warning on save.

@implementer(IValidator)
@adapter(Interface, ICollectionFilterBrowserLayer, Interface, IField, Interface)
class TargetCollectionValidator(validator.SimpleFieldValidator):
    def validate(self, value):
        super(TargetCollectionValidator, self).validate(value)
        portlet = False
        if value:
            obj = aq_inner(uuidToCatalogBrain(value)).getObject()
        else:
            for obj in aq_chain(self.context):
                if IPortletAssignmentMapping.providedBy(obj):
                    portlet = True
                if IDexterityContent.providedBy(obj):
                    break
        collection = queryAdapter(obj, ICollectionish)
        # if it's a tile we will use a warning instead since we can't tell if a listing tile
        # has been added to the layout yet as it's not saved.
        if portlet and (collection is None or collection.content_selector is None):
            raise Invalid(
                _(u"Context is not a collection or has a contentlisting tile, please set a target.")
            )
        return True


validator.WidgetValidatorDiscriminators(
    TargetCollectionValidator, field=ICollectionFilterBaseSchema["target_collection"],
)
