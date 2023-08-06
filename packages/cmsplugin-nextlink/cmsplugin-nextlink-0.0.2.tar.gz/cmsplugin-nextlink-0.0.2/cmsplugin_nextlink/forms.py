from django import forms
from django.db import models
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.core.validators import URLValidator, EmailValidator, validate_email
from django.core.exceptions import ValidationError 

from cmsplugin_nextlink.models import NextLink
from cmsplugin_nextlink.utils import is_integer


class NextLinkForm(forms.ModelForm):

    class Meta:
        model = NextLink

    def clean(self):
        cleaned_data = super(NextLinkForm, self).clean()
        protocol = cleaned_data.get("protocol")
        # check protocol depencies
        if "mailto" in protocol:
            if cleaned_data.get("link_url"):
                msg = _(u"URL is not allowed in combination with mailto protocol.")
                self._errors["link_url"] = self.error_class([msg])
                del cleaned_data["link_url"]
            if not cleaned_data.get("mailto_address"):
                msg = _(u"Mailto address is missing.")
                self._errors["mailto_address"] = self.error_class([msg])
            if not cleaned_data.get("mailto_subject"):
                msg = _(u"Mailto subject is missing.")
                self._errors["mailto_subject"] = self.error_class([msg])
            try:
                #validate_email = EmailValidator()
                validate_email(str(cleaned_data["mailto_address"]))
            except ValidationError, e:
                self._errors["mailto_address"] = self.error_class([str("%s" % e)])
                del cleaned_data["mailto_address"]
        elif "picture" in protocol:
            if cleaned_data.get("link_url"):
                msg = _(u"URL is not allowed in combination with picture protocol.")
                self._errors["link_url"] = self.error_class([msg])
                del cleaned_data["link_url"]
            if cleaned_data.get("mailto_address"):
                msg = _(u"Mailto address is not allowed in combination with picture protocol.")
                self._errors["mailto_address"] = self.error_class([msg])
                del cleaned_data["mailto_address"]
            if not cleaned_data.get("image"):
                msg = _(u"Image is missing.")
                self._errors["image"] = self.error_class([msg])
        else:
            if cleaned_data.get("mailto_address"):
                msg = _(u"Mailto address is not allowed in combination with internal or external protocol.")
                self._errors["mailto_address"] = self.error_class([msg])
                del cleaned_data["mailto_address"]
            if cleaned_data.get("mailto_subject"):
                msg = _(u"Maitlo subject is not allowd in combination with internal or external protocol.")
                self._errors["mailto_subject"] = self.error_class([msg])
                del cleaned_data["mailto_subject"]
            if not cleaned_data.get("link_url"):
                msg = _(u"URL is missing.")
                self._errors["link_url"] = self.error_class([msg])
            if "external" in protocol:
                try:
                    validate_url = URLValidator(verify_exists=False)
                    validate_url(str(cleaned_data["link_url"]))
                except ValidationError, e:
                    msg = _(u"The give url has not a valid format.")
                    self._errors["link_url"] = self.error_class([msg])
                    del cleaned_data["link_url"]
        return cleaned_data 
