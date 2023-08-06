import datetime

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cmsplugin_nextlink.models import NextLink


def is_link_expired(link_expired):
    """Return boolean.
    Simple check if the link is expired.
    If return True then its not displayed anymore as link.
    Is used <s>{{ name }}</s> tag to deactivating.
    """
    if datetime.datetime.now() > link_expired:
        return True
    else:
        return False


class NextLinkPlugin(CMSPluginBase):
   
    model = NextLink
    name = _("NextLink")
    render_template = "cmsplugin_nextlink/nextlink_plugin.html"
    text_enabled = True

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
            'placeholder': placeholder,
            'object': instance,
        })
        return context

    def icon_src(self, instance):
        return settings.STATIC_URL + u"cms/images/plugins/link.png"


plugin_pool.register_plugin(NextLinkPlugin)
