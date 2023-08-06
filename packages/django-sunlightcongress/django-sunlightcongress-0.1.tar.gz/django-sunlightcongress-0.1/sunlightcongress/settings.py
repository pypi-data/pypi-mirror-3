from os import environ

from django.utils.translation import ugettext as _

from sunlight.config import KEY_ENVVAR


try:
    SUNLIGHT_API_KEY = environ[KEY_ENVVAR]
except KeyError:
    raise EnvironmentError(_('%s environment variable not set') % KEY_ENVVAR)
