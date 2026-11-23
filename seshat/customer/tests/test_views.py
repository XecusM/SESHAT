from django.test import TestCase
from django.urls import reverse

from customer.models import CustomerCompany, Customer
from seshat.testing import (
                        create_user, create_superuser,
                        create_customer_company, create_customer, )


class CompanyViewsTest(TestCase):
    '''
    Test the company views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())

    def test_create(self):
        response = self.client.post(reverse('customer:NewCompany'), {'name': 'Acme'})
        company = CustomerCompany.objects.get(name='Acme')
        self.assertRedirects(response, company.get_absolute_url())
        self.assertEqual(company.get_activities().count(), 1)

    def test_edit(self):
        company = create_customer_company('Old')
        self.client.post(reverse('customer:EditCompany', kwargs={'pk': company.pk}),
                         {'name': 'New', 'tax_code': 'TX-1'})
        company.refresh_from_db()
        self.assertEqual((company.name, company.tax_code), ('New', 'TX-1'))

    def test_list_search_and_details(self):
        create_customer_company('Alpha')
        company = create_customer_company('Beta')
        create_customer(company=company, first_name='Bea')
        response = self.client.get(reverse('customer:CompaniesList'), {'search': 'bet'})
        self.assertEqual(list(response.context['object_list']), [company])
        self.assertContains(self.client.get(company.get_absolute_url()), 'Bea')

    def test_delete(self):
        company = create_customer_company()
        response = self.client.post(reverse('customer:DeleteCompany', kwargs={'pk': company.pk}))
        self.assertRedirects(response, reverse('customer:CompaniesList'))
        self.assertFalse(CustomerCompany.objects.exists())

    def test_delete_company_with_contacts(self):
        contact = create_customer()
        response = self.client.post(
                    reverse('customer:DeleteCompany', kwargs={'pk': contact.company.pk}))
        self.assertTemplateUsed(response, 'error_message.html')

    def test_delete_requires_post(self):
        company = create_customer_company()
        response = self.client.get(reverse('customer:DeleteCompany', kwargs={'pk': company.pk}))
        self.assertEqual(response.status_code, 405)


class ContactViewsTest(TestCase):
    '''
    Test the contact views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())
        self.company = create_customer_company()

    def test_create_with_company_preselected(self):
        response = self.client.get(reverse('customer:NewCustomer'), {'company': self.company.pk})
        self.assertEqual(str(response.context['form'].initial['company']), str(self.company.pk))
        response = self.client.post(
                    reverse('customer:NewCustomer') + f'?next={self.company.get_absolute_url()}',
                    {'company': self.company.pk, 'first_name': 'Ann', 'last_name': 'Lee'})
        self.assertRedirects(response, self.company.get_absolute_url())
        self.assertTrue(Customer.objects.filter(first_name='Ann').exists())

    def test_edit_and_details(self):
        contact = create_customer(company=self.company)
        self.client.post(reverse('customer:EditCustomer', kwargs={'pk': contact.pk}),
                         {'company': self.company.pk, 'first_name': 'New', 'last_name': 'Name',
                          'job': 'Buyer'})
        contact.refresh_from_db()
        self.assertEqual(contact.full_name, 'New Name')
        self.assertContains(self.client.get(contact.get_absolute_url()), 'Buyer')

    def test_list_search(self):
        create_customer(company=self.company, first_name='Zara')
        create_customer(company=self.company, first_name='Omar')
        response = self.client.get(reverse('customer:CustomersList'), {'search': 'zar'})
        self.assertEqual([c.first_name for c in response.context['object_list']], ['Zara'])

    def test_delete(self):
        contact = create_customer(company=self.company)
        response = self.client.post(reverse('customer:DeleteCustomer', kwargs={'pk': contact.pk}))
        self.assertRedirects(response, reverse('customer:CustomersList'))
        self.assertFalse(Customer.objects.exists())


class PermissionsTest(TestCase):
    '''
    Test the customer permissions
    '''

    def test_view_only(self):
        company = create_customer_company()
        self.client.force_login(create_user(permissions=['customer.view_customercompany']))
        self.assertEqual(self.client.get(reverse('customer:CompaniesList')).status_code, 200)
        self.assertEqual(self.client.get(reverse('customer:CustomersList')).status_code, 403)
        self.assertEqual(self.client.get(reverse('customer:NewCompany')).status_code, 403)
        self.assertEqual(self.client.post(
                reverse('customer:DeleteCompany', kwargs={'pk': company.pk})).status_code, 403)

    def test_anonymous(self):
        response = self.client.get(reverse('customer:CompaniesList'))
        self.assertEqual(response.status_code, 302)
