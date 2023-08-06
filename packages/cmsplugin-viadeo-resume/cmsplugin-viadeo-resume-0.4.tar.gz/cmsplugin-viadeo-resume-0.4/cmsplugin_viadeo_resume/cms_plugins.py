from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _
from django.conf import settings
from viadeoapi import ViadeoConnector

class ViadeoResumePlugin(CMSPluginBase):
    name = _("Viadeo resume plugin")
    render_template = "cmsplugin_viadeo_resume/resume.html"

    def render(self, context, instance, placeholder):
        vc = ViadeoConnector(settings.VIADEO_CLIENT_ID, 
                             settings.VIADEO_CLIENT_SECRET,
                             settings.VIADEO_ACCESS_TOKEN)
        context.update(dict(profile=vc.profile(), educations=vc.educations()))
        return context

plugin_pool.register_plugin(ViadeoResumePlugin)
