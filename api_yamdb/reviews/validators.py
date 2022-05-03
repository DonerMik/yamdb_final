import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def year_validator(value):
    if value > datetime.datetime.now().year or value < -1000:
        raise ValidationError(
            _('%(value)s is not a correcrt year!'),
            params={'value': value},
        )
