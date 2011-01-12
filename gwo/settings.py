from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

GWO_ACCOUNT = getattr(settings, 'GWO_ACCOUNT', None)
if GWO_ACCOUNT is None:
    raise ImproperlyConfigured("Django-GWO is missing the GWO_ACCOUNT setting.")

GWO_USER = getattr(settings, 'GWO_USER', None)
if GWO_USER is None:
    raise ImproperlyConfigured("Django-GWO is missing the GWO_USER setting.")

GWO_PASSWORD = getattr(settings, 'GWO_PASSWORD', None)
if GWO_USER is None:
    raise ImproperlyConfigured("Django-GWO is missing the GWO_PASSWORD setting.")

