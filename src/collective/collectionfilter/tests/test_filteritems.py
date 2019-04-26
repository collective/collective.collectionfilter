# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from collective.collectionfilter.testing import COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING  # noqa
from collective.collectionfilter.filteritems import get_filter_items
from plone.supermodel import model
from zope.interface import provider
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import SchemaInvalidatedEvent
from zope.component import queryUtility

def get_data_by_val(result, val):
    for r in result:
        if r['value'] == val:
            return r

class TestFilteritems(unittest.TestCase):

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.collection = self.portal['testcollection']
        self.collection_uid = self.collection.UID()

    def test_filteritems(self):
        self.assertEqual(len(self.collection.results()), 2)

        result = get_filter_items(
            self.collection_uid, 'Subject', cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, 'all')['count'], 2)
        self.assertEqual(get_data_by_val(result, 'all')['selected'], True)
        self.assertEqual(get_data_by_val(result, u'Süper')['count'], 2)
        self.assertEqual(get_data_by_val(result, u'Evänt')['count'], 1)
        self.assertEqual(get_data_by_val(result, u'Dokumänt')['count'], 1)

        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Süper'},
            cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, u'Süper')['selected'], True)

        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Dokumänt'},
            cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, u'Dokumänt')['selected'], True)  # noqa

        # test narrowed down results
        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Dokumänt'},
            narrow_down=True,
            cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, u'Dokumänt')['selected'], True)  # noqa
        self.assertEqual(get_data_by_val(result, u'all')['count'], 1)

    def test_portal_type_filter(self):
        self.assertEqual(len(self.collection.results()), 2)

        result = get_filter_items(
            self.collection_uid, 'portal_type', cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, 'all')['count'], 2)
        self.assertEqual(get_data_by_val(result, 'all')['selected'], True)
        self.assertEqual(get_data_by_val(result, u'Event')['count'], 1)
        self.assertEqual(get_data_by_val(result, u'Document')['count'], 1)

        result = get_filter_items(
            self.collection_uid, 'portal_type',
            request_params={'portal_type': u'Event'},
            cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, u'Event')['selected'], True)

        result = get_filter_items(
            self.collection_uid, 'portal_type',
            request_params={'portal_type': u'Event'},
            narrow_down=True,
            cache_enabled=False)

        self.assertEqual(len(result), 2)
        self.assertEqual(get_data_by_val(result, u'all')['count'], 1)
        self.assertEqual(get_data_by_val(result, u'Event')['selected'], True)

    def test_human_readable_title(self):
        self.assertEqual(len(self.collection.results()), 2)


        from zope.interface import implementer
        from zope.interface import Interface
        from plone.app.contenttypes.content import Document
        from plone.behavior.interfaces import IBehaviorAssignable
        from zope.component import adapter
        from zope.interface import implementer

        # define the vocabulary
        items = [ ('value1', u'Value 1 title'), ('value2', u'Value 2 title')]
        terms = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items ]
        dummy_vocabulary = SimpleVocabulary(terms)


        # Field with a vocabulary
        @provider(IFormFieldProvider)
        class IDummyVocabField(model.Schema):
            dummy = schema.Choice(title=u"Dummy",
                                       vocabulary=dummy_vocabulary
                                        )

        # register field as a behavior
        from plone.behavior.registration import BehaviorRegistration
        from zope.component import provideAdapter
        registration = BehaviorRegistration(
               title=u"Dummy Vocab Field",
               description=u"Provides vocab field",
               interface=IDummyVocabField,
               marker=None,
               factory=None)

        
    
        @adapter(Document)
        @implementer(IBehaviorAssignable)
        class TestingAssignable(object):
     
            enabled = [IDummyVocabField]
            def __init__(self, context):
                self.context = context
     
            def supports(self, behavior_interface):
                return behavior_interface in self.enabled
     
            def enumerate_behaviors(self):
                for e in self.enabled:
                    yield queryUtility(IBehavior, name=e.__identifier__)

        provideAdapter(TestingAssignable)

        import pdb;pdb.set_trace()
        # make document support the behavior
        IDummyVocabField(doc)

       
        # get result from collection
        result = get_filter_items(
            self.collection_uid, group_by='Dummy', 
            fetch_human_readable_title=True,
            cache_enabled=False)

