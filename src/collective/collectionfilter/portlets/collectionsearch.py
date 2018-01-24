# -*- coding: utf-8 -*-
from .. import _
from ..interfaces import ICollectionSearchSchema
from ..utils import base_query
from ..utils import safe_decode
from ..utils import safe_encode
from ..vocabularies import TEXT_IDX
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlet.collection.collection import Renderer as CollectionRenderer
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import urlencode
from zope import schema
from zope.component import queryUtility
from zope.interface import implements


PLONE5 = getFSVersionTuple()[0] >= 5

if PLONE5:
    base_AddForm = base.AddForm
    base_EditForm = base.EditForm
else:
    from plone.app.portlets.browser.z3cformhelper import AddForm as base_AddForm  # noqa
    from plone.app.portlets.browser.z3cformhelper import EditForm as base_EditForm  # noqa
    from z3c.form import field


class ICollectionSearchPortlet(ICollectionSearchSchema, IPortletDataProvider):

    header = schema.TextLine(
        title=_('label_header', default=u'Portlet header'),
        description=_(
            'help_header',
            u'Title of the rendered portlet.'
        ),
        required=False,
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
        return self.collection.title

    @property
    def filterClassName(self):
        if self.data.header:
            name = queryUtility(IIDNormalizer).normalize(self.data.header)
            return u'filter' + name.capitalize()
        return ''

    @property
    def id(self):
        portlethash = self.request.form.get(
            'portlethash',
            getattr(self, '__portlet_metadata__', {}).get('hash', '')
        )
        return portlethash

    @property
    def reload_url(self):
        reload_url = '{0}/@@render-portlet?portlethash={1}'.format(
            self.context.absolute_url(),
            self.id
        )
        return reload_url

    @property
    def value(self):
        return safe_unicode(self.request.get(TEXT_IDX, ''))

    @property
    def action_url(self):
        return self.collection.absolute_url()

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
    def ajax_url(self):
        # Recursively transform all to unicode
        request_params = safe_decode(self.request.form)
        request_params.update({'x': 'y'})  # ensure at least one val is set
        urlquery = base_query(request_params, extra_ignores=['SearchableText'])
        ajax_url = u'{0}/?{1}'.format(
            self.collection.absolute_url(),
            urlencode(safe_encode(urlquery), doseq=True)
        )
        return ajax_url

    @property
    def collection(self):
        if not self._collection:
            self._collection = uuidToObject(
                self.data.target_collection
            )
        return self._collection

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
