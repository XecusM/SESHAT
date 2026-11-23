from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PurchaseConfig(AppConfig):
    name = 'purchase'
    verbose_name = _('Purchases')
