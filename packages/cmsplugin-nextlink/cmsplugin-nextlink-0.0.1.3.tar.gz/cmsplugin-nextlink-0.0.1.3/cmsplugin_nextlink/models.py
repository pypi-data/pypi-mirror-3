import os
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cms.models import CMSPlugin

from cmsplugin_nextlink.utils import PROTOCOLS
from cmsplugin_nextlink.validator import validator_url


class NextLink(CMSPlugin):
    """Define the attribute for database.
    FIXME: think about imagefield if the link is klickable with an image
    """
    # maybe could be set up of a fix date
    date_in_the_future = datetime.datetime.now() + datetime.timedelta(days=365000)
    name = models.CharField(_("Name"), max_length=256,
        help_text=_("The name of the link for displaying on the webpage."))
    protocol = models.CharField(_("Protocol"), max_length=8, choices=PROTOCOLS, 
        default="internal", null=True,
        help_text=_("Choose a protocol or use internal as default."))
    url = models.CharField(_("Url"), max_length=256, 
        help_text=_("Enter the url, if it for internal use then just the path. "
                    "Otherwise use valid URL."))
    title = models.CharField(_("Title"), max_length=256, null=True, blank=True,
        help_text=_("Optional set a title for the link name, if empty the name is used."))
    access_key = models.CharField(_("Access key"), max_length=1, null=True, blank=True,
        help_text=_("Optional set an accesskey. For example letter a for keystroke 'a'."))
    link_create = models.DateTimeField(_('link created'), blank=True,
        auto_now=True,
        help_text=_("Set the date of creation."))
    link_expired = models.DateTimeField(_('link expired'), blank=True, 
        default=date_in_the_future, 
        help_text=_("Set the date of expired, if is set and date is equal the link "
                  "is not working anymore."))
    image = models.ImageField(_("Image"), upload_to="nextlink_archive", 
        null=True, blank=True,
        help_text = _("Choose an image to make it clickable"))
    alt_attribute = models.CharField(_("alt"), null=True, blank=True,
        max_length=256,
        help_text = _("Optional set an alt attibute for the image"))

    def clean(self):
        validator_url(self.protocol, self.url)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return unicode(self)
