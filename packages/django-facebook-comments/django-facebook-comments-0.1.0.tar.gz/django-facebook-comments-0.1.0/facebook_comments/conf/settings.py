from django.conf import settings
from django.utils.translation import to_locale


LOCALE = getattr(settings, 'FACEBOOK_LOCALE', to_locale(settings.LANGUAGE_CODE))
