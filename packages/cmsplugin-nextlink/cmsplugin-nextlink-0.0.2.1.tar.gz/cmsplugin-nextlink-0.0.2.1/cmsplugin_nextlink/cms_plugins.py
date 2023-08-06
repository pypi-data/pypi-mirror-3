from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from cmsplugin_nextlink.models import NextLink
from cmsplugin_nextlink.forms import NextLinkForm
from cmsplugin_nextlink.utils import is_link_expired


class NextLinkPlugin(CMSPluginBase):
    model = NextLink 
    form = NextLinkForm
    name = _("NextLink")
    render_template = "cmsplugin_nextlink/nextlink_plugin.html"
    text_enabled = True
    fieldsets = [
        (None, {"fields": 
            ["name", 
             "description", 
             "protocol"]}),
        (_("Protocol options"), {"fields": 
            ["link_url", 
             "mailto_address", 
             "image"]}),
        (_("Standard optional attributes"), {"fields": 
            ["link_attr_title", 
             "image_attr_alt", 
             "link_attr_accesskey", 
             "link_attr_tabindex",
             "mailto_subject"], "classes": ["collapse"]}),
        (_("Optional attribues"), {"fields": 
            ["link_attr_class", 
             "link_attr_id", 
             "link_attr_dir", 
             "link_attr_charset", 
             "link_attr_style", 
             "link_attr_name"], "classes": ["collapse"]}),
        (_("Expired information"), {"fields": 
            ["link_expired"], "classes": ["collapse"]}),
    ]

    def render(self, context, instance, placeholder):
        n = instance.nextlink
        z = [n.link_attr_id, n.link_attr_id, n.link_attr_style, n.link_attr_name, 
            n.link_attr_class, n.link_attr_tabindex]

        #raise RuntimeError(z)
        if "internal" in instance.nextlink.protocol:
            if not instance.nextlink.link_url.startswith("/"):
                url = "/" + instance.nextlink.link_url
            else:
                url = instance.nextlink.link_url
        elif "mailto" in instance.nextlink.protocol:
            url = "mailto:" + instance.nextlink.mailto_address + "?subject=" + instance.nextlink.mailto_subject
        else:
            url = instance.nextlink.link_url
        if "picture" in instance.nextlink.protocol:
            picture = True
        else:
            picture = False
        context.update({
            "attr_id": instance.nextlink.link_attr_id,
            "attr_name": instance.nextlink.link_attr_name,
            "attr_class": instance.nextlink.link_attr_class,
            "attr_style": instance.nextlink.link_attr_style,
            'picture': picture,
            'name': instance.nextlink.name,
            'url': url,
            'title': instance.nextlink.link_attr_title,
            'accesskey': instance.nextlink.link_attr_accesskey,
            'tabindex': instance.nextlink.link_attr_tabindex,
            'link_expired': is_link_expired(instance.nextlink.link_expired),
            'image': instance.nextlink.image,
            'alt': instance.nextlink.image_attr_alt,
            'media_url': settings.MEDIA_URL,
            'object': instance,
            'placeholder': placeholder,
        })
        return context

    def icon_src(self, instance):
        return settings.STATIC_URL + u"cms/images/plugins/link.png"


plugin_pool.register_plugin(NextLinkPlugin)
