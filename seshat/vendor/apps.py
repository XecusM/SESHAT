from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VendorConfig(AppConfig):
    name = 'vendor'
    verbose_name = _('Vendors')
