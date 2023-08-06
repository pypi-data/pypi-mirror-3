from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import ugettext_lazy as _

from cmsplugin_nextlink.utils import PROTOCOLS


def validator_tab_index(value):
    if value > 10:
         raise ValidationError(_(u'You can only use a range from 0 to 9.'))

def validator_url(which_protocol, url_to_validate):
    """Check if the url does not have some protocol"""
    validate_url = URLValidator(verify_exists=False)
    if "internal" not in which_protocol:
        url = which_protocol + "://" + url_to_validate
    else:
        # use localhost as domain name
        for protocol in PROTOCOLS:
            if protocol[0] in url_to_validate:
                raise ValidationError(_(u'Wrong input for url. Make sure that you don\'t use something like http:// in your url. [%s]' % url_to_validate))
        if not url_to_validate.startswith("/"):
            url = "http://localhost/" + url_to_validate
        else:
            url = "http://localhost" + url_to_validate
    try:
        validate_url(url)
    except ValidationError, e:
        raise ValidationError(_(u'Wrong input for url. Make sure that you don\'t use something like http:// in your url. [%s]' % url))
    return True
    
