from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from customer import models, views


class CustomerViewsTests(TestCase):
    '''
    Test all views for customer application
    '''
    def setUp(self):
        '''
        Intiate tests
        '''
        self.user = get_user_model().objects.create_user(
                                                username='user',
                                                password='testpassword')

        self.company = models.CustomerCompany.objects.create(
                                                name='New Company')

        self.customer = models.Customer.objects.create(
                                                company=self.company,
                                                first_name='Mohamed',
                                                last_name='Aboel-fotouh')

        self.company_new_url = reverse('customer:company_new')
        self.company_edit_url = reverse(
                            'customer:company_edit',
                            kwargs={'pk': self.company.id})
        self.company_details_url = reverse(
                            'customer:company_details',
                            kwargs={'pk': self.company.id})
        self.companies_list_url = reverse(
                            'customer:companies_list')
        self.company_delete_url = reverse(
                            'customer:company_delete',
                            kwargs={'pk': self.company.id})

        self.customer_new_url = reverse(
                            'customer:customer_new',
                            kwargs={'pk': self.company.id})
        self.customer_edit_url = reverse(
                            'customer:customer_edit',
                            kwargs={'pk': self.customer.id})
        self.customer_details_url = reverse(
                            'customer:customer_details',
                            kwargs={'pk': self.customer.id})
        self.customers_list_url = reverse(
                            'customer:customers_list')
        self.customer_delete_url = reverse(
                            'customer:customer_delete',
                            kwargs={'pk': self.customer.id})

    def test_new_company_get(self):
        '''
        Test get url for creating new company
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='add_customercompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.company_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/company_new.html')

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
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='add_customercompany',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {'name': 'Another Company', }

        response = self.client.post(self.company_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.CustomerCompany.objects.all().count(), 2)

    def test_edit_company_get(self):
        '''
        Test get url for creating edit company
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='change_customercompany',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.company_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/company_edit.html')

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
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='change_customercompany',
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
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='view_customercompany',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.company_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/company_details.html')

    def test_companies_list_get(self):
        '''
        Test get url for companies list
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='view_customercompany',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.companies_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/companies_list.html')

    def test_company_delete_get(self):
        '''
        Test get url for company delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='delete_customercompany',
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
        Test post url for company delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.CustomerCompany)
        permission = Permission.objects.get(
                                    codename='delete_customercompany',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.post(self.company_delete_url)

        self.assertEqual(response.status_code, 200)

        company = models.CustomerCompany.objects.create(name='Another company')

        self.assertEqual(models.CustomerCompany.objects.all().count(), 2)

        response = self.client.post(reverse(
                                            'customer:company_delete',
                                            kwargs={'pk': company.id}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.CustomerCompany.objects.all().count(), 1)

    def test_new_customer_get(self):
        '''
        Test get url for creating new customer
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        permission = Permission.objects.get(
                                    codename='add_customer',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.customer_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/customer_new.html')

    def test_new_customer_permission(self):
        '''
        Test permissions for creating new customer
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.customer_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_customer_post(self):
        '''
        Test post url for creating new customer
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        permission = Permission.objects.get(
                                    codename='add_customer',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'company': self.company.id,
                    'first_name': 'Osama',
                    'last_name': 'Aboel-fotouh',
                }

        response = self.client.post(self.customer_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.Customer.objects.all().count(), 2)

    def test_edit_customer_get(self):
        '''
        Test get url for creating edit customer
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        permission = Permission.objects.get(
                                    codename='change_customer',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.customer_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/customer_edit.html')

    def test_edit_customer_permission(self):
        '''
        Test permissions for creating edit customer
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.customer_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_customer_post(self):
        '''
        Test post url for creating edit customer
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        permission = Permission.objects.get(
                                    codename='change_customer',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'company': self.company.id,
                    'first_name': 'Osama',
                    'last_name': 'Aboel-fotouh',
                }

        response = self.client.post(self.customer_edit_url, data=payload)

        self.customer.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.customer.first_name, payload['first_name'])

    def test_customer_details_get(self):
        '''
        Test get url for customer details
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        permission = Permission.objects.get(
                                    codename='view_customer',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.customer_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/customer_details.html')

    def test_customers_list_get(self):
        '''
        Test get url for customers list
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        permission = Permission.objects.get(
                                    codename='view_customer',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.customers_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'customer/customers_list.html')

    def test_customer_delete_get(self):
        '''
        Test get url for customer delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        permission = Permission.objects.get(
                                    codename='delete_customer',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.customer_delete_url)

        self.assertEqual(response.status_code, 404)

    def test_customer_delete_permission(self):
        '''
        Test permissions for customer delete
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.customer_delete_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_customer_post(self):
        '''
        Test post url for creating customer delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Customer)
        delete_permission = Permission.objects.get(
                                    codename='delete_customer',
                                    content_type=content_type)
        self.user.user_permissions.add(delete_permission)
        view_permission = Permission.objects.get(
                                    codename='view_customer',
                                    content_type=content_type)
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.post(self.customer_delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Customer.objects.all().count(), 0)
