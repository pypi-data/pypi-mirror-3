from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _

from models import GGSubscribe

class SubscribePlugin(CMSPluginBase):
    model = GGSubscribe
    name = _("Google groups subscription")
    render_template = "cmsplugin_googlegroups_widgets/subscribe.html"

    def render(self, context, instance, placeholder):
        context["instance"] = instance
        return context

plugin_pool.register_plugin(SubscribePlugin)
