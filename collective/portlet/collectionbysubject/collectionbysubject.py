

from time import time

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.schema.interfaces import ISource, IContextSourceBinder

from plone.memoize import ram
from plone.memoize.instance import memoize
from plone.memoize.compress import xhtml_compress
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlet.collection.collection import Renderer as CollectionRenderer

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IATTopic
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.collectionbysubject import CollectionBySubjectMessageFactory as _


from config import SUBJECT_TO_INDEX # add new indexes as neccessary



class ICollectionBySubject(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        required=False,
        description=_(u"Title of the rendered portlet it will override collection's title."))

    target_collection = schema.Choice(
        title=_(u"Target collection"),
        description=_(u"Find the collection which provides the items to list"),
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides' : IATTopic.__identifier__},
            default_query='path:'))

    group_by = schema.Choice(
        title=_(u"Group by"),
        description=_(u"Select subject you wish to group collection results by."),
        required=True,
        values = SUBJECT_TO_INDEX.keys(),)

    cache_duration = schema.TextLine(
        title=_(u"Cache duration"),
        description=_(u"How long do you want portlet results to be cached (in minutes)?."),
        default=u'60')


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ICollectionBySubject)

    header = u""
    target_collection=None
    group_by=u"Keywords"

    def __init__(self, header=u"", target_collection=None,
                    group_by=u"Keywords", cache_duration=u"60"):
        self.header = header
        self.target_collection = target_collection
        self.group_by = group_by
        self.cache_duration = cache_duration

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        if self.header:
            return self.header
        else:
            return _(u'Collection By Subject')

def render_cachekey(method, self):
   return time() // (int(self.data.cache_duration) * 60)


class Renderer(CollectionRenderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    _template = ViewPageTemplateFile('collectionbysubject.pt')
   
    def header_url(self):
        collection = self.collection(self.data.target_collection)
        if collection is None:
            return None
        else:
            return collection.absolute_url()

    def header_title(self):
        if self.data.header:
            return self.data.header
        
        collection = self.collection(self.data.target_collection)
        if collection is None:
            return None
        else:
            return collection.Title()

    @ram.cache(render_cachekey)
    def render(self):
        if self.available:
            return xhtml_compress(self._template())
        else:
            return ''
    
    def results(self):
        """ Get the actual result brains from the collection. 
            This is a wrapper so that we can memoize if and only if we aren't
            selecting random items."""
        results = []
        collection = self.collection(self.data.target_collection)
        if collection is not None:
            results = collection.queryCatalog({})
            if results:
                grouped_results = {}
                for item in results:
                    if self.data.group_by == 'Keywords':
                        for keyword in getattr(item, SUBJECT_TO_INDEX[self.data.group_by]):
                            grouped_results.setdefault(keyword, [])
                            grouped_results[keyword].append(item)
                    else:
                        subject = getattr(item, SUBJECT_TO_INDEX[self.data.group_by])
                        grouped_results.setdefault(subject, [])
                        grouped_results[subject].append(item)
                results = []
                translation = getToolByName(self.context, 'translation_service')
                for subject, items in grouped_results.iteritems():
                    results.append(dict(
                        title   = subject,
                        url     = collection.absolute_url() + '/?' + \
                                    SUBJECT_TO_INDEX[self.data.group_by] + \
                                    '=' + subject,
                        number  = len(items)))
        return results

    @memoize
    def collection(self, collection_path=None):
        """ get the collection the portlet is pointing to"""
        
        if collection_path is None:
            collection_path = self.data.target_collection
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]
        
        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(collection_path, default=None)

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ICollectionBySubject)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    label = _(u"Add Collection by subject Portlet")
    description = _(u"This portlet display a listing of items from "
                     "a Collection that are grouped by selected subject.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ICollectionBySubject)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    label = _(u"Add Collection by subject Portlet")
    description = _(u"This portlet display a listing of items from a Collection "
                     "that are grouped by selected subject.")


