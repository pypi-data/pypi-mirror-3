# coding: utf-8

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import SliderPlugin
from django.utils.translation import ugettext_lazy as _


class CMSSliderPlugin(CMSPluginBase):
    model = SliderPlugin
    name = _('Slider')
    render_template = 'nivo/slider.html'
    text_enabled = False
    admin_preview = False

    def render(self, context, instance, placeholder):
        context.update({
            'object': instance,
            'placeholder': placeholder,
            'images': instance.images,
        })
        return context

plugin_pool.register_plugin(CMSSliderPlugin)
