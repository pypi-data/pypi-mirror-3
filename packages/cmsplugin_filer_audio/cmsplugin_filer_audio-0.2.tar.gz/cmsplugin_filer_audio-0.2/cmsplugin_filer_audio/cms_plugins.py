from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cmsplugin_filer_audio.models import FilerAudioPlugin as FilerAudioPluginModel
from django.utils.translation import ugettext as _


class FilerAudioPlugin(CMSPluginBase):
    model = FilerAudioPluginModel # Model where data about this plugin is saved
    name = _("Audio") # Name of the plugin
    render_template = "cmsplugin_filer_audio/plugin.html" # template to render the plugin with

    def render(self, context, instance, placeholder):
        context.update({'instance':instance})
        return context


plugin_pool.register_plugin(FilerAudioPlugin) # register the plugin
