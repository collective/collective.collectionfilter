from plone.app.portlets.portlets.base import Renderer
from plone.base.utils import get_top_request
from plone.base.utils import safe_text


class BasePortletRenderer(Renderer):
    @property
    def filter_id(self):
        request = get_top_request(self.request)
        portlethash = request.form.get(
            "portlethash", getattr(self, "__portlet_metadata__", {}).get("hash", "")
        )
        return portlethash

    @property
    def reload_url(self):
        reload_url = "{}/@@render-portlet?portlethash={}".format(
            self.context.absolute_url(),
            safe_text(self.filter_id),
        )
        return reload_url

    @property
    def available(self):
        return self.is_available
