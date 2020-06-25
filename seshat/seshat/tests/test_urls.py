from django.test import TestCase
from django.urls import reverse, resolve

from seshat import views


class SeshatUrlsTest(TestCase):
    '''
    Test all urls in the seshat applciation
    '''
    def test_index_resolved(self):
        '''
        Test new order url
        '''
        url = reverse('index')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.Index)

    def test_backup_resolved(self):
        '''
        Test backup url
        '''
        url = reverse('backup')
        self.assertEquals(
                        resolve(url).func,
                        views.databackup)

    def test_download_backup_resolved(self):
        '''
        Test download backup url
        '''
        url = reverse('download_backup', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.databackup_download)

    def test_restore_resolved(self):
        '''
        Test restore url
        '''
        url = reverse('restore')
        self.assertEquals(
                        resolve(url).func,
                        views.datarestore)

    def test_export_resolved(self):
        '''
        Test export url
        '''
        url = reverse('export')
        self.assertEquals(
                        resolve(url).func,
                        views.dataexport)

    def test_import_download_template_resolved(self):
        '''
        Test download template url for import
        '''
        url = reverse('download_template', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.dataimport_template)
