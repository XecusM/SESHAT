from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.utils import translation

from seshat import urls, views


class ProjectUrlsTest(SimpleTestCase):
    '''
    Test the project urls
    '''

    def test_urls(self):
        cases = [
            ('Index', views.index, None),
            ('Backup', views.backup, None),
            ('DownloadBackup', views.backup_download, {'file_name': 'SESHATdb-1.json'}),
            ('Restore', views.restore, None),
            ('Export', views.export_data, None),
            ('Import', views.import_data, None),
            ('ImportTemplate', views.import_template, {'module': 'stock.Item'}),
        ]
        for name, view, kwargs in cases:
            self.assertEqual(resolve(reverse(name, kwargs=kwargs)).func, view, name)

    def test_language_prefix(self):
        with translation.override('en'):
            self.assertEqual(reverse('Index'), '/')
        with translation.override('ar'):
            self.assertEqual(reverse('Index'), '/ar/')
            self.assertEqual(reverse('stock:Index'), '/ar/stock/')

    def test_set_language_url(self):
        self.assertEqual(reverse('set_language'), '/i18n/setlang/')

    def test_error_handlers(self):
        self.assertEqual(urls.handler400, views.error_400)
        self.assertEqual(urls.handler403, views.error_403)
        self.assertEqual(urls.handler404, views.error_404)
        self.assertEqual(urls.handler500, views.error_500)
