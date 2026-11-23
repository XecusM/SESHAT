import json
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, override_settings
from django.urls import reverse

from x_django_app.models import XActivity

from customer.models import CustomerCompany
from purchase.models import PurchaseOrder
from sale.models import SaleOrder
from seshat import views
from seshat.testing import (
                        TempDirsTestCase, create_user, create_superuser,
                        create_stock, create_vendor_company,
                        create_customer_company, )
from stock.models import Category


class IndexViewTest(TempDirsTestCase):
    '''
    Test the project dashboard
    '''

    def test_login_required(self):
        response = self.client.get(reverse('Index'))
        self.assertRedirects(response, '/admin/login/?next=/', fetch_redirect_response=False)

    def test_dashboard(self):
        item = create_stock(code='LOW', stock_limit=5)
        order = PurchaseOrder.objects.create(company=create_vendor_company())
        order.set_items([{'item': item, 'quantity': 3, 'price': 2}])
        sale = SaleOrder.objects.create(company=create_customer_company())
        sale.set_items([{'item': item, 'quantity': 1, 'price': 4}])
        self.client.force_login(create_user())
        response = self.client.get(reverse('Index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items_count'], 1)
        self.assertEqual(response.context['low_stock_count'], 1)
        self.assertEqual(response.context['stock_value'], 20)
        self.assertEqual(response.context['orders_count'], 2)
        chart = json.loads(response.context['chart_data'])
        self.assertEqual(chart['purchases'][-1], 6)
        self.assertEqual(chart['sales'][-1], 4)
        self.assertEqual(list(response.context['company_list']),
                         list(CustomerCompany.objects.all()))


class BackupRestoreViewsTest(TempDirsTestCase):
    '''
    Test backup, download, delete and restore
    '''

    def setUp(self):
        self.admin = create_superuser()
        self.client.force_login(self.admin)

    def test_permissions(self):
        self.client.force_login(create_user())
        for name in ['Backup', 'Restore', 'Export', 'Import']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403, name)

    def test_backup_download_delete_restore(self):
        Category.objects.create(name='Backed')
        response = self.client.post(reverse('Backup'), {'backup': ''})
        self.assertRedirects(response, reverse('Backup'))
        files = os.listdir(settings.BACKUP_DIR)
        self.assertEqual(len(files), 1)
        file_name = files[0]
        self.assertTrue(file_name.startswith(settings.DUMPDATA_FILENAME))

        response = self.client.get(reverse('Backup'))
        self.assertEqual(response.context['files'], [file_name])

        response = self.client.get(reverse('DownloadBackup', kwargs={'file_name': file_name}))
        content = b''.join(response.streaming_content)
        response.close()
        self.assertIn(b'Backed', content)

        Category.objects.all().delete()
        response = self.client.post(reverse('Restore'), {
                'restoring_file': SimpleUploadedFile(file_name, content, 'application/json')})
        self.assertRedirects(response, reverse('Restore'))
        self.assertTrue(Category.objects.filter(name='Backed').exists())
        self.assertTrue(XActivity.objects.filter(activity=XActivity.RESTORE).exists())

        response = self.client.post(reverse('Backup'), {'delete': '', 'files': [file_name]})
        self.assertEqual(os.listdir(settings.BACKUP_DIR), [])

    def test_download_unknown_file(self):
        response = self.client.get(reverse('DownloadBackup', kwargs={'file_name': '..passwd'}))
        self.assertEqual(response.status_code, 404)

    def test_restore_invalid_file(self):
        response = self.client.post(reverse('Restore'), {
                'restoring_file': SimpleUploadedFile('bad.txt', b'x')})
        self.assertRedirects(response, reverse('Restore'))
        response = self.client.post(reverse('Restore'), {
                'restoring_file': SimpleUploadedFile('bad.json', b'not json')})
        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertTrue(any("Can't restore" in m for m in messages))


class ExportImportViewsTest(TempDirsTestCase):
    '''
    Test exporting and importing CSV files
    '''

    def setUp(self):
        self.client.force_login(create_superuser())

    def test_pages(self):
        for name in ['Export', 'Import']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertIn(('stock.Item', 'Items'),
                          [(key, str(label)) for key, label in response.context['modules']])

    def test_export(self):
        Category.objects.create(name='Tools')
        response = self.client.post(reverse('Export'), {'module': 'stock.Category'})
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('categories.csv', response['Content-Disposition'])
        self.assertEqual(response.content.decode().splitlines(), ['name', 'Tools'])

    def test_export_unknown(self):
        response = self.client.post(reverse('Export'), {'module': 'auth.User'})
        self.assertRedirects(response, reverse('Export'))

    def test_import(self):
        upload = SimpleUploadedFile('c.csv', b'name\nscrews\nnails\n', 'text/csv')
        response = self.client.post(reverse('Import'), {
                                'module': 'stock.Category', 'importing_file': upload})
        self.assertRedirects(response, reverse('Import'))
        self.assertEqual(Category.objects.count(), 2)

    def test_import_bad_file(self):
        upload = SimpleUploadedFile('c.csv', b'wrong\nx\n', 'text/csv')
        response = self.client.post(reverse('Import'), {
                                'module': 'stock.Category', 'importing_file': upload})
        self.assertRedirects(response, reverse('Import'))
        self.assertEqual(Category.objects.count(), 0)

    def test_import_missing_module(self):
        response = self.client.post(reverse('Import'), {'module': 'nope'})
        self.assertRedirects(response, reverse('Import'))

    def test_import_template(self):
        response = self.client.get(reverse('ImportTemplate', kwargs={'module': 'vendor.Vendor'}))
        self.assertTrue(response.content.decode().startswith('company,first_name'))
        response = self.client.get(reverse('ImportTemplate', kwargs={'module': 'bad.Module'}))
        self.assertEqual(response.status_code, 404)


class ErrorViewsTest(TempDirsTestCase):
    '''
    Test the error handlers render the styled pages
    '''

    def test_handlers(self):
        request = RequestFactory().get('/')
        request.user = create_user()
        for handler, status in [(views.error_400, 400), (views.error_403, 403),
                                (views.error_404, 404), (views.error_405, 405)]:
            response = handler(request, Exception())
            self.assertEqual(response.status_code, status)
            self.assertIn(str(status).encode(), response.content)
        self.assertEqual(views.error_500(request).status_code, 500)

    @override_settings(DEBUG=False)
    def test_404_page(self):
        response = self.client.get('/no-such-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'error/404.html')

    @override_settings(DEBUG=False)
    def test_405_page(self):
        self.client.force_login(create_user())
        response = self.client.get(reverse('account:Logout'))
        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, 'error/405.html')
        self.assertEqual(response['Allow'], 'POST, OPTIONS')

    @override_settings(DEBUG=False)
    def test_403_page(self):
        self.client.force_login(create_user())
        response = self.client.get(reverse('Backup'))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'error/403.html')
