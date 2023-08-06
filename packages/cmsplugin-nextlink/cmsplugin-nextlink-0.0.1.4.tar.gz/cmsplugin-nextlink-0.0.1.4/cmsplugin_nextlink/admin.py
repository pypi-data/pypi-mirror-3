import datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

#from cms.admin.placeholderadmin import PlaceholderAdmin

from cmsplugin_nextlink.models import NextLink
from cmsplugin_nextlink.utils import is_link_expired, set_default_link_expired_date


def make_link_expired(modeladmin, request, queryset):
    queryset.update(link_expired=datetime.datetime.now())
make_link_expired.short_description = _("Mark selected next links as expired")


def make_link_active(modeladmin, request, queryset):
    queryset.update(link_expired=set_default_link_expired_date())
make_link_active.short_description = _("Mark selected next links as active")


class NextLinkAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'link_created', 'link_expired', 'description']
    fieldsets = [
        (None, {"fields": ["name", "protocol", "url", "title"]}),
        (_("Link information"), {"fields": ["access_key"], "classes": ["collapse"]}),
        (_("Image setup"), {"fields": ["image", "alt_attribute"], 'classes': ['collapse']}),
        (_("Expired information"), {"fields": ["link_expired"], "classes": ["collapse"]}),
        (_("Description interanl"), {"fields": ["description"], "classes": ["collapse"]}),
    ]
    actions = [make_link_expired, make_link_active]


admin.site.register(NextLink, NextLinkAdmin)
