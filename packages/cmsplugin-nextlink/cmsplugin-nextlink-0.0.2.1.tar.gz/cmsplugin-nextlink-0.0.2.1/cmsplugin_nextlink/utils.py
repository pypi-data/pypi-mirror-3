import re
import datetime

from django.utils.translation import ugettext_lazy as _


PROTOCOLS = (
    ("internal", _("internal")),
    ("external", _("external")),
    ("mailto", _("mailto")),
    ("picture", _("picture")),
)

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


def set_default_link_expired_date():
    """Return datetime object.
    Set the date for the link far in the future.
    """
    # maybe could be set up of a fix date
    date_in_the_future = datetime.datetime.now() + datetime.timedelta(days=365000)
    return date_in_the_future   

def is_integer(integer_value):
    """Pseudo interger testing."""
    if not re.match(r"[0-9]+", integer_value):
        return False
    else:
        return True

   
