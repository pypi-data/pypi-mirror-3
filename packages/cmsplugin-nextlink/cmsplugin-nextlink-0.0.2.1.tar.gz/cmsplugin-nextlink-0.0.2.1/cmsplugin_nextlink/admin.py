import datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
#from cms.admin.placeholderadmin import PlaceholderAdmin

from cmsplugin_nextlink.models import NextLink
from cmsplugin_nextlink.forms import NextLinkForm
from cmsplugin_nextlink.utils import (is_link_expired, 
    set_default_link_expired_date)


def make_link_expired(modeladmin, request, queryset):
    queryset.update(link_expired=datetime.datetime.now())
make_link_expired.short_description = _("Mark selected next links as expired")

def make_link_active(modeladmin, request, queryset):
    queryset.update(link_expired=set_default_link_expired_date())
make_link_active.short_description = _("Mark selected next links as active")

class NextLinkAdmin(admin.ModelAdmin):
    form = NextLinkForm
    list_display = ['id','name', 'link_created', 'link_expired', 'description']
    actions = [make_link_expired, make_link_active]

    fieldsets = (
        (None, {"fields": 
            ["name", 
             "description", 
             "protocol"]}),
        (_("Protocol options: Use only only of this fields below:"), {"fields": 
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
    )

admin.site.register(NextLink, NextLinkAdmin)
