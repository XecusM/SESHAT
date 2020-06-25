from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class SeshatViewsTests(TestCase):
    '''
    Test all views for stock application
    '''
    def setUp(self):
        '''
        Intiate tests
        '''
        self.user = get_user_model().objects.create_user(
                                                username='user',
                                                password='testpassword')

        self.index_url = reverse('index')

        self.backup_url = reverse('backup')
        self.restore_url = reverse('restore')
        self.export_url = reverse('export')
        self.import_url = reverse('import')

    def test_index_get(self):
        '''
        Test get url for index page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'seshat/index.html')

    def test_backup_get(self):
        '''
        Test get url for backup page
        '''
        content_type = ContentType.objects.get_for_model(get_user_model())
        permission = Permission.objects.get(
                                    codename='backup',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.backup_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'seshat/backup.html')

    def test_backup_permission(self):
        '''
        Test permissions for backup page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.backup_url)

        self.assertEqual(response.status_code, 403)

    def test_restore_get(self):
        '''
        Test get url for restore page
        '''
        content_type = ContentType.objects.get_for_model(get_user_model())
        permission = Permission.objects.get(
                                    codename='restore',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.restore_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'seshat/restore.html')

    def test_restore_permission(self):
        '''
        Test permissions for restore page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.restore_url)

        self.assertEqual(response.status_code, 403)

    def test_export_get(self):
        '''
        Test get url for export page
        '''
        content_type = ContentType.objects.get_for_model(get_user_model())
        permission = Permission.objects.get(
                                    codename='export',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'seshat/export.html')

    def test_export_permission(self):
        '''
        Test permissions for export page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, 403)

    def test_import_get(self):
        '''
        Test get url for import page
        '''
        content_type = ContentType.objects.get_for_model(get_user_model())
        permission = Permission.objects.get(
                                    codename='import',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'seshat/import.html')

    def test_import_permission(self):
        '''
        Test permissions for import page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 403)
