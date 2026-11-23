from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SaleConfig(AppConfig):
    name = 'sale'
    verbose_name = _('Sales')
