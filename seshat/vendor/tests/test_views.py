from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from vendor import models, views


class VendorViewsTests(TestCase):
    '''
    Test all views for vendor application
    '''
    def setUp(self):
        '''
        Intiate tests
        '''
        self.user = get_user_model().objects.create_user(
                                                username='user',
                                                password='testpassword')

        self.company = models.VendorCompany.objects.create(name='New Company')

        self.vendor = models.Vendor.objects.create(
                                                company=self.company,
                                                first_name='Mohamed',
                                                last_name='Aboel-fotouh')

        self.company_new_url = reverse('vendor:company_new')
        self.company_edit_url = reverse(
                            'vendor:company_edit',
                            kwargs={'pk': self.company.id})
        self.company_details_url = reverse(
                            'vendor:company_details',
                            kwargs={'pk': self.company.id})
        self.companies_list_url = reverse(
                            'vendor:companies_list')
        self.company_delete_url = reverse(
                            'vendor:company_delete',
                            kwargs={'pk': self.company.id})

        self.vendor_new_url = reverse(
                            'vendor:vendor_new',
                            kwargs={'pk': self.company.id})
        self.vendor_edit_url = reverse(
                            'vendor:vendor_edit',
                            kwargs={'pk': self.vendor.id})
        self.vendor_details_url = reverse(
                            'vendor:vendor_details',
                            kwargs={'pk': self.vendor.id})
        self.vendors_list_url = reverse(
                            'vendor:vendors_list')
        self.vendor_delete_url = reverse(
                            'vendor:vendor_delete',
                            kwargs={'pk': self.vendor.id})

    def test_new_company_get(self):
        '''
        Test get url for creating new company
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='add_vendorcompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.company_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/company_new.html')

    def test_new_company_permission(self):
        '''
        Test permissions for creating new company
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.company_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_company_post(self):
        '''
        Test post url for creating new company
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='add_vendorcompany',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {'name': 'Another Company', }

        response = self.client.post(self.company_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.VendorCompany.objects.all().count(), 2)

    def test_edit_company_get(self):
        '''
        Test get url for creating edit company
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='change_vendorcompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.company_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/company_edit.html')

    def test_edit_company_permission(self):
        '''
        Test permissions for creating edit company
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.company_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_company_post(self):
        '''
        Test post url for creating edit company
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='change_vendorcompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {'name': 'Another Company', }

        response = self.client.post(self.company_edit_url, data=payload)

        self.company.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.company.name, payload['name'])

    def test_company_details_get(self):
        '''
        Test get url for company details
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='view_vendorcompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.client.force_login(self.user)

        response = self.client.get(self.company_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/company_details.html')

    def test_companies_list_get(self):
        '''
        Test get url for companies list
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='view_vendorcompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.client.force_login(self.user)

        response = self.client.get(self.companies_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/companies_list.html')

    def test_company_delete_get(self):
        '''
        Test get url for company delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='delete_vendorcompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.company_delete_url)

        self.assertEqual(response.status_code, 404)

    def test_company_delete_permission(self):
        '''
        Test permissions for company delete
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.company_delete_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_company_post(self):
        '''
        Test post url for creating company delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.VendorCompany)
        permission = Permission.objects.get(
                                    codename='delete_vendorcompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.post(self.company_delete_url)

        self.assertEqual(response.status_code, 200)

        company = models.VendorCompany.objects.create(name='Another company')

        self.assertEqual(models.VendorCompany.objects.all().count(), 2)

        response = self.client.post(reverse(
                                            'vendor:company_delete',
                                            kwargs={'pk': company.id}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.VendorCompany.objects.all().count(), 1)

    def test_new_vendor_get(self):
        '''
        Test get url for creating new vendor
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='add_vendor',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.vendor_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/vendor_new.html')

    def test_new_vendor_permission(self):
        '''
        Test permissions for creating new vendor
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.vendor_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_vendor_post(self):
        '''
        Test post url for creating new vendor
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='add_vendor',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'company': self.company.id,
                    'first_name': 'Osama',
                    'last_name': 'Aboel-fotouh',
                }

        response = self.client.post(self.vendor_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.Vendor.objects.all().count(), 2)

    def test_edit_vendor_get(self):
        '''
        Test get url for creating edit vendor
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='change_vendor',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.vendor_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/vendor_edit.html')

    def test_edit_vendor_permission(self):
        '''
        Test permissions for creating edit vendor
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.vendor_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_vendor_post(self):
        '''
        Test post url for creating edit vendor
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='change_vendor',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'company': self.company.id,
                    'first_name': 'Osama',
                    'last_name': 'Aboel-fotouh',
                }

        response = self.client.post(self.vendor_edit_url, data=payload)

        self.vendor.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.vendor.first_name, payload['first_name'])

    def test_vendor_details_get(self):
        '''
        Test get url for vendor details
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='view_vendor',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.client.force_login(self.user)

        response = self.client.get(self.vendor_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/vendor_details.html')

    def test_vendors_list_get(self):
        '''
        Test get url for vendors list
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='view_vendor',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)
        
        self.client.force_login(self.user)

        response = self.client.get(self.vendors_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'vendor/vendors_list.html')

    def test_vendor_delete_get(self):
        '''
        Test get url for vendor delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='delete_vendor',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.vendor_delete_url)

        self.assertEqual(response.status_code, 404)

    def test_vendor_delete_permission(self):
        '''
        Test permissions for vendor delete
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.vendor_delete_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_vendor_post(self):
        '''
        Test post url for creating vendor delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Vendor)
        permission = Permission.objects.get(
                                    codename='delete_vendor',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.post(self.vendor_delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Vendor.objects.all().count(), 0)
