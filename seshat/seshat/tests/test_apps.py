from django.apps import apps
from django.test import SimpleTestCase


class AppConfigsTest(SimpleTestCase):
    '''
    Every SESHAT application is installed with its translated name
    '''

    def test_app_configs(self):
        expected = {
            'seshat': 'SESHAT',
            'account': 'Administration',
            'stock': 'Stock',
            'customer': 'Customers',
            'vendor': 'Vendors',
            'purchase': 'Purchases',
            'sale': 'Sales',
        }
        for label, name in expected.items():
            config = apps.get_app_config(label)
            self.assertEqual(config.name, label)
            self.assertEqual(str(config.verbose_name), name)

    def test_asgi_wsgi(self):
        from seshat import asgi, wsgi
        self.assertTrue(callable(asgi.application))
        self.assertTrue(callable(wsgi.application))
