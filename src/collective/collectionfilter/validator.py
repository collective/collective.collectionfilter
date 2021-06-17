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


@implementer(IValidator)
@adapter(Interface, ICollectionFilterBrowserLayer, Interface, IField, Interface)
class TargetCollectionValidator(validator.SimpleFieldValidator):
    def validate(self, value):
        super(TargetCollectionValidator, self).validate(value)

        if value:
            obj = aq_inner(uuidToCatalogBrain(value)).getObject()
        else:
            for obj in aq_chain(self.context):
                if IDexterityContent.providedBy(obj):
                    break
        collection = queryAdapter(obj, ICollectionish)
        if collection is None:
            raise Invalid(
                _(u"Context is not a collection or has a contentlisting tile, please set a target collection.")
            )
        return True


validator.WidgetValidatorDiscriminators(
    TargetCollectionValidator, field=ICollectionFilterBaseSchema["target_collection"]
)
