from . import msgFact as _
from .vocabularies import TEXT_IDX
from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.app.vocabularies.catalog import CatalogSource
from plone.portlet.collection.collection import Renderer as CollectionRenderer
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.interface import implements

PLONE5 = getFSVersionTuple()[0] >= 5

if PLONE5:
    base_AddForm = base.AddForm
    base_EditForm = base.EditForm
else:
    from plone.app.portlets.browser.z3cformhelper import AddForm as base_AddForm  # noqa
    from plone.app.portlets.browser.z3cformhelper import EditForm as base_EditForm  # noqa
    from z3c.form import field


class ICollectionSearchPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_('label_header', default=u'Portlet header'),
        description=_(
            'help_header',
            u'Title of the rendered portlet.'
        ),
        required=False,
    )

    target_collection = schema.Choice(
        title=_(u'label_target_collection', default=u'Target Collection'),
        description=_(
            u'help_target_collection',
            default=u'The collection, which is the source for the filter '
                    u'items and where the filter is applied.'
        ),
        required=True,
        source=CatalogSource(
            object_provides=ISyndicatableCollection.__identifier__
        ),
    )


class Assignment(base.Assignment):
    implements(ICollectionSearchPortlet)

    header = u""
    target_collection = None

    def __init__(
        self,
        header=u"",
        target_collection=None,
    ):
        self.header = header
        self.target_collection = target_collection

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u'Collection Search')


class Renderer(CollectionRenderer):
    render = ViewPageTemplateFile('collectionsearch.pt')

    _collection = None

    @property
    def available(self):
        return True

    @property
    def header_title(self):
        if self.data.header:
            return self.data.header
        return self.collection.Title if self.collection else None

    @property
    def value(self):
        return safe_unicode(self.request.get(TEXT_IDX, ''))

    @property
    def action_url(self):
        return self.collection.getURL()

    @property
    def urlquery(self):
        urlquery = {}
        urlquery.update(self.request.form)
        for it in (TEXT_IDX, 'b_start', 'b_size', 'batch', 'sort_on', 'limit'):
            # Remove problematic url parameters
            if it in urlquery:
                del urlquery[it]
        return urlquery

    @property
    def collection(self):
        item = self._collection
        if not item:
            self._collection = item = uuidToCatalogBrain(
                self.data.target_collection
            )
        return item

    def update(self):
        pass


class AddForm(base_AddForm):
    if PLONE5:
        schema = ICollectionSearchPortlet
    else:
        fields = field.Fields(ICollectionSearchPortlet)

    label = _(u"Add Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base_EditForm):
    if PLONE5:
        schema = ICollectionSearchPortlet
    else:
        fields = field.Fields(ICollectionSearchPortlet)

    label = _(u"Edit Collection Search Portlet")
    description = _(
        u"This portlet allows fulltext search in collection results."
    )
