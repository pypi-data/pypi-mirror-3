import datetime

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from cmsplugin_nextlink.models import NextLink
from cmsplugin_nextlink.utils import is_link_expired


class NextLinkPlugin(CMSPluginBase):
   
    model = NextLink
    name = _("NextLink")
    render_template = "cmsplugin_nextlink/nextlink_plugin.html"
    text_enabled = True
    fieldsets = [
        (None, {"fields": ["name", "protocol", "url", "title"]}),
        (_("Link information"), {"fields": ["access_key"], "classes": ["collapse"]}),
        (_("Image setup"), {"fields": ["image", "alt_attribute"], 'classes': ['collapse']}),
        (_("Expired information"), {"fields": ["link_expired"], "classes": ["collapse"]}),
        (_("Description interanl"), {"fields": ["description"], "classes": ["collapse"]}),
    ]

    def render(self, context, instance, placeholder):
        if "internal" in instance.nextlink.protocol:
            if not instance.nextlink.url.startswith("/"):
                url = "/" + instance.nextlink.url
            else:
                url = instance.nextlink.url
        else:
            url = instance.nextlink.protocol + "://" + instance.nextlink.url
        if len(instance.nextlink.title) > 0:
            title = instance.nextlink.title
        else:
            title = instance.nextlink.name 
        if instance.nextlink.access_key:
            access_key = instance.nextlink.access_key
        else:
            access_key = False
        if instance.nextlink.image:
            image = instance.nextlink.image
        else:
            image = False
        if instance.nextlink.alt_attribute:
            alt = instance.nextlink.alt_attibute
        else:
            alt = instance.nextlink.name
        context.update({
            'name': instance.nextlink.name,
            'url': url,
            'title': title,
            'access_key': access_key,
            'link_expired': is_link_expired(instance.nextlink.link_expired),
            'image': image,
            'alt': alt,
            'media_url': settings.MEDIA_URL,
            'object': instance,
            'placeholder': placeholder,
        })
        return context

    def icon_src(self, instance):
        return settings.STATIC_URL + u"cms/images/plugins/link.png"


plugin_pool.register_plugin(NextLinkPlugin)
