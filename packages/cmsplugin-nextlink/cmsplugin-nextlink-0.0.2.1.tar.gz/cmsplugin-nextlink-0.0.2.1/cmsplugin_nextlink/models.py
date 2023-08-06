import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

from cmsplugin_nextlink.utils import PROTOCOLS, set_default_link_expired_date
from cmsplugin_nextlink.validator import validator_uri


class NextLink(CMSPlugin):
    """Define the attribute for database."""
    choices_tabindex = [(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), 
        (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9")]
    choices_dir = [("rtl", "rtl"), ("ltr", "ltr")]
    name = models.CharField(_("Name"), 
        max_length=256,
        help_text=_("The name of the link for displaying on the webpage."))
    description = models.CharField(_("description"),
        max_length=256, null=True, blank=True,
        help_text = _("Optional, give a short description for the admin page."))
    protocol = models.CharField(_("Protocol"), 
        max_length=8, 
        choices=PROTOCOLS, default="internal",
        help_text=_("Choose a protocol, targets are 'internal' or 'external' "
                    "for links or 'mailto' to add this a link target "
                    "or 'picture' to display an image only."))
    link_url = models.CharField(_("URL"), 
        max_length=256, null=True, blank=True, 
        help_text=_("Enter the URL, if it for internal use then just the path. "
                    "Otherwise use valid URL."))
    mailto_address = models.CharField(_("Mailto"),
        max_length=256, null=True, blank=True,
        help_text=_("Fully qualified email address."))
    mailto_subject = models.CharField(_("mailto subject"),
        max_length=256, null=True, blank=True,
        help_text=_("Optional, set an subject for mailto."))
    link_attr_title = models.CharField(_("Attribute title"), 
        max_length=256, null=True, blank=True,
        help_text=_("Optional, specifies extra information about an element "
                    "set a title for the link name, if empty the name is used."))
    link_attr_accesskey = models.CharField(_("Attribute accesskey"), 
        max_length=3, null=True, blank=True,
        help_text=_("Optional, specifies a keyboard shortcut to access an element."))
    link_attr_tabindex = models.PositiveIntegerField(_("Attribute tabindex"), 
        null=True, blank=True,
        choices=choices_tabindex,
        help_text = _("Optional, specifies the tab order of an element."))
    link_attr_class = models.CharField(_("Attribute class"), 
        max_length=256, null=True, blank=True,
        help_text=_("Optional, specifies a classname for an element."))
    link_attr_id = models.CharField(_("Attribute id"), 
        max_length=256, null=True, blank=True,
        help_text=_("Optional, specifies a unique id for an element set a link id."))
    link_attr_dir = models.CharField(_("Attribute dir"), 
        max_length=256, null=True, choices=choices_dir, default="rtl",
        help_text=_("Optional, specifies the text direction for the "
                    "content in an element."))
    link_attr_charset = models.CharField(_("Attribute charset"), 
        max_length=256, null=True, blank=True,
        help_text=_("Optional, specifies the character encoding of the "
                    "resource designated by the link."))
    link_attr_style = models.CharField(_("Attribute style"),
        max_length=256, null=True, blank=True,
        help_text=_("Optional, specifies an inline style for an element."))
    link_attr_name = models.CharField(_("Attribute name"),
        max_length=256, null=True, blank=True,
        help_text=_("Optional, specifies the name of an anchor."))
    link_created = models.DateTimeField(_('link created'), 
        blank=True, auto_now=True)
    link_expired = models.DateTimeField(_('link expired'), 
        blank=True, default=set_default_link_expired_date(), 
        help_text=_("Set the date of expired, if is set and date is equal "
                    "the link is not working anymore."))
    image = models.ImageField(_("Image"), upload_to="nextlink_archive", 
        null=True, blank=True,
        help_text = _("Choose an image to make the link clickable. "
                      "If you want only display an image set the "
                      "expired time to now."))
    image_attr_alt = models.CharField(_("Attribute alt"), 
        max_length=256, null=True, blank=True,
        help_text = _("Optional set an alt attibute for the image"))
    
    def save(self, *args, **kwargs):
        if not self.link_attr_title:
            self.link_attr_title = self.name
        if self.image and not self.image_attr_alt:
            self.image_attr_alt = self.name
        super(NextLink, self).save()
    
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return unicode(self)
