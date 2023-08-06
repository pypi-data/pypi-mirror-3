import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, EmailValidator
from django.utils.translation import ugettext_lazy as _

from cmsplugin_nextlink.utils import PROTOCOLS



def validator_uri(which_protocol, uri_to_validate):
    """Check if the url does not have some protocol"""
    #raise RuntimeError(which_protocol, uri_to_validate[0])
    if "mailto" in which_protocol:
        return True
    for protocol in PROTOCOLS:
        if protocol[0] in uri_to_validate:
            raise ValidationError(_(u'Wrong input for uri. Make sure that you don\'t use something like http:// in your url. [%s]' % uri_to_validate))
    
    validate_uri = URLValidator(verify_exists=False)
    if ("internal" or "mailto") not in which_protocol:
        uri = which_protocol + "://" + uri_to_validate
    else:
        if "internal" in which_protocol:
            # use localhost as domain name
           if not uri_to_validate.startswith("/"):
                uri = "http://localhost/" + uri_to_validate
           else:
                uri = "http://localhost" + uri_to_validate
    try:
        validate_uri(uri)
    except ValidationError, e:
        raise ValidationError(_(u"%s [%s]" % (str(e), uri)))
    return True

