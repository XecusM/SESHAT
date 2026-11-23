from django.test import TestCase
from django.urls import reverse

from vendor.models import VendorCompany, Vendor
from seshat.testing import (
                        create_user, create_superuser,
                        create_vendor_company, create_vendor, )


class CompanyViewsTest(TestCase):
    '''
    Test the company views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())

    def test_create(self):
        response = self.client.post(reverse('vendor:NewCompany'), {'name': 'Acme'})
        company = VendorCompany.objects.get(name='Acme')
        self.assertRedirects(response, company.get_absolute_url())
        self.assertEqual(company.get_activities().count(), 1)

    def test_edit(self):
        company = create_vendor_company('Old')
        self.client.post(reverse('vendor:EditCompany', kwargs={'pk': company.pk}),
                         {'name': 'New', 'tax_code': 'TX-1'})
        company.refresh_from_db()
        self.assertEqual((company.name, company.tax_code), ('New', 'TX-1'))

    def test_list_search_and_details(self):
        create_vendor_company('Alpha')
        company = create_vendor_company('Beta')
        create_vendor(company=company, first_name='Bea')
        response = self.client.get(reverse('vendor:CompaniesList'), {'search': 'bet'})
        self.assertEqual(list(response.context['object_list']), [company])
        self.assertContains(self.client.get(company.get_absolute_url()), 'Bea')

    def test_delete(self):
        company = create_vendor_company()
        response = self.client.post(reverse('vendor:DeleteCompany', kwargs={'pk': company.pk}))
        self.assertRedirects(response, reverse('vendor:CompaniesList'))
        self.assertFalse(VendorCompany.objects.exists())

    def test_delete_company_with_contacts(self):
        contact = create_vendor()
        response = self.client.post(
                    reverse('vendor:DeleteCompany', kwargs={'pk': contact.company.pk}))
        self.assertTemplateUsed(response, 'error_message.html')

    def test_delete_requires_post(self):
        company = create_vendor_company()
        response = self.client.get(reverse('vendor:DeleteCompany', kwargs={'pk': company.pk}))
        self.assertEqual(response.status_code, 405)


class ContactViewsTest(TestCase):
    '''
    Test the contact views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())
        self.company = create_vendor_company()

    def test_create_with_company_preselected(self):
        response = self.client.get(reverse('vendor:NewVendor'), {'company': self.company.pk})
        self.assertEqual(str(response.context['form'].initial['company']), str(self.company.pk))
        response = self.client.post(
                    reverse('vendor:NewVendor') + f'?next={self.company.get_absolute_url()}',
                    {'company': self.company.pk, 'first_name': 'Ann', 'last_name': 'Lee'})
        self.assertRedirects(response, self.company.get_absolute_url())
        self.assertTrue(Vendor.objects.filter(first_name='Ann').exists())

    def test_edit_and_details(self):
        contact = create_vendor(company=self.company)
        self.client.post(reverse('vendor:EditVendor', kwargs={'pk': contact.pk}),
                         {'company': self.company.pk, 'first_name': 'New', 'last_name': 'Name',
                          'job': 'Buyer'})
        contact.refresh_from_db()
        self.assertEqual(contact.full_name, 'New Name')
        self.assertContains(self.client.get(contact.get_absolute_url()), 'Buyer')

    def test_list_search(self):
        create_vendor(company=self.company, first_name='Zara')
        create_vendor(company=self.company, first_name='Omar')
        response = self.client.get(reverse('vendor:VendorsList'), {'search': 'zar'})
        self.assertEqual([c.first_name for c in response.context['object_list']], ['Zara'])

    def test_delete(self):
        contact = create_vendor(company=self.company)
        response = self.client.post(reverse('vendor:DeleteVendor', kwargs={'pk': contact.pk}))
        self.assertRedirects(response, reverse('vendor:VendorsList'))
        self.assertFalse(Vendor.objects.exists())


class PermissionsTest(TestCase):
    '''
    Test the vendor permissions
    '''

    def test_view_only(self):
        company = create_vendor_company()
        self.client.force_login(create_user(permissions=['vendor.view_vendorcompany']))
        self.assertEqual(self.client.get(reverse('vendor:CompaniesList')).status_code, 200)
        self.assertEqual(self.client.get(reverse('vendor:VendorsList')).status_code, 403)
        self.assertEqual(self.client.get(reverse('vendor:NewCompany')).status_code, 403)
        self.assertEqual(self.client.post(
                reverse('vendor:DeleteCompany', kwargs={'pk': company.pk})).status_code, 403)

    def test_anonymous(self):
        response = self.client.get(reverse('vendor:CompaniesList'))
        self.assertEqual(response.status_code, 302)
