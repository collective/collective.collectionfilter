from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseFilterView
from collective.collectionfilter.interfaces import ICollectionFilterSchema
from collective.collectionfilter.portlets import BasePortletRenderer
from collective.collectionfilter.vocabularies import DEFAULT_FILTER_TYPE
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


class ICollectionFilterPortlet(ICollectionFilterSchema, IPortletDataProvider):
    """Portlet interface based on ICollectionFilterSchema"""


@implementer(ICollectionFilterPortlet)
class Assignment(base.Assignment):
    header = ""
    target_collection = None
    group_by = ""
    show_count = False
    cache_enabled = True
    filter_type = DEFAULT_FILTER_TYPE
    input_type = "links"
    narrow_down = False
    view_name = None
    content_selector = "#content-core"
    hide_if_empty = False
    reverse = False
    # list_scaling = None

    def __init__(
        self,
        header="",
        target_collection=None,
        group_by="",
        show_count=False,
        cache_enabled=True,
        filter_type=DEFAULT_FILTER_TYPE,
        input_type="links",
        narrow_down=False,
        view_name=None,
        content_selector="#content-core",
        hide_if_empty=False,
        reverse=False,
        # list_scaling=None
    ):
        self.header = header
        self.target_collection = target_collection
        self.group_by = group_by
        self.show_count = show_count
        self.cache_enabled = cache_enabled
        self.filter_type = filter_type
        self.input_type = input_type
        self.narrow_down = narrow_down
        self.view_name = view_name
        self.content_selector = content_selector
        self.hide_if_empty = hide_if_empty
        self.reverse = reverse
        # self.list_scaling = list_scaling

    @property
    def portlet_id(self):
        """Return the portlet assignment's unique object id."""
        return id(self)

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _("Collection Filter")


class Renderer(BasePortletRenderer, BaseFilterView):
    render = ViewPageTemplateFile("collectionfilter.pt")


class AddForm(base.AddForm):
    schema = ICollectionFilterPortlet
    label = _("Add Collection Filter Portlet")
    description = _(
        "This portlet shows grouped criteria of collection results and "
        "allows filtering of collection results."
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    schema = ICollectionFilterPortlet
    label = _("Edit Collection Filter Portlet")
    description = _(
        "This portlet shows grouped criteria of collection results and "
        "allows filtering of collection results."
    )
