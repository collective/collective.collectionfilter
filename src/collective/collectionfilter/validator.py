# -*- coding: utf-8 -*-
from Acquisition import aq_base, aq_inner
from plone.dexterity.interfaces import IDexterityContent
from z3c.form import validator
from z3c.form.interfaces import IValidator
from zope.component import adapter, getMultiAdapter, queryUtility
from zope.interface import Interface, Invalid, implementer
from zope.schema.interfaces import IField

from collective.collectionfilter import _
from collective.collectionfilter.interfaces import (
    ICollectionFilterBaseSchema, ICollectionFilterBrowserLayer)


@implementer(IValidator)
@adapter(Interface, ICollectionFilterBrowserLayer, Interface, IField, Interface)
class TargetCollectionValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        super(TargetCollectionValidator, self).validate(value)

        # breakpoint()

        if IDexterityContent.providedBy(self.context):
            context = self.context
        else:
            context = self.context.aq_parent
        if not hasattr(aq_base(context), 'query'):
            raise Invalid(_(u'Context is not a collection, please set a target collection.'))
        return True


validator.WidgetValidatorDiscriminators(TargetCollectionValidator,
                                        field=ICollectionFilterBaseSchema['target_collection'])
