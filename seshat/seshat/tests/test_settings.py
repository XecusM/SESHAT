import os
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from seshat import seshat_settings


class SettingsTest(SimpleTestCase):
    '''
    Test the project settings
    '''

    def test_core_settings(self):
        self.assertEqual(settings.AUTH_USER_MODEL, 'account.User')
        self.assertEqual(settings.LOGIN_URL, '/admin/login/')
        self.assertEqual(settings.CRISPY_TEMPLATE_PACK, 'bootstrap5')
        self.assertEqual([code for code, _ in settings.LANGUAGES], ['en', 'ar'])
        self.assertTrue(settings.USE_I18N)
        self.assertTrue(settings.USE_TZ)

    def test_installed_apps(self):
        for app in ['x_django_app', 'django_db_logger', 'crispy_bootstrap5',
                    'account.apps.AccountConfig', 'stock.apps.StockConfig',
                    'customer.apps.CustomerConfig', 'vendor.apps.VendorConfig',
                    'purchase.apps.PurchaseConfig', 'sale.apps.SaleConfig']:
            self.assertIn(app, settings.INSTALLED_APPS)
        self.assertNotIn('report.apps.ReportConfig', settings.INSTALLED_APPS)

    def test_context_processors(self):
        processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        self.assertIn('seshat.middleware.theme', processors)
        self.assertIn('seshat.middleware.debug', processors)

    def test_data_folders(self):
        for name in ['BACKUP_DIR', 'RESTORE_DIR', 'IMPORT_DIR', 'EXPORT_DIR']:
            self.assertTrue(str(getattr(settings, name)).startswith(str(settings.VAR_DIR)))


class LocalSettingsTest(SimpleTestCase):
    '''
    Test the environment helpers of seshat_settings
    '''

    def test_env(self):
        with mock.patch.dict(os.environ, {'SESHAT_TEST_VALUE': 'abc'}):
            self.assertEqual(seshat_settings.env('SESHAT_TEST_VALUE'), 'abc')
        self.assertEqual(seshat_settings.env('SESHAT_MISSING_VALUE', 'x'), 'x')

    def test_env_bool(self):
        for value, expected in [('true', True), ('1', True), ('yes', True),
                                ('false', False), ('0', False)]:
            with mock.patch.dict(os.environ, {'SESHAT_TEST_BOOL': value}):
                self.assertEqual(seshat_settings.env_bool('SESHAT_TEST_BOOL'), expected)
        self.assertTrue(seshat_settings.env_bool('SESHAT_MISSING_BOOL', True))

    def test_env_list(self):
        with mock.patch.dict(os.environ, {'SESHAT_TEST_LIST': "'a.com', b.com,"}):
            self.assertEqual(seshat_settings.env_list('SESHAT_TEST_LIST'), ['a.com', 'b.com'])
        self.assertEqual(seshat_settings.env_list('SESHAT_MISSING_LIST', ['x']), ['x'])
