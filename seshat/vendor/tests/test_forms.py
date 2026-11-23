from django.test import TestCase

from vendor.forms import CompanyForm, VendorForm
from seshat.testing import create_vendor_company


class CompanyFormTest(TestCase):
    '''
    Test the company form
    '''

    def test_valid(self):
        form = CompanyForm(data={'name': 'Acme', 'phone': '+201234567890',
                                 'website': 'https://acme.example.com'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid(self):
        form = CompanyForm(data={'name': '', 'phone': '12'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('phone', form.errors)


class ContactFormTest(TestCase):
    '''
    Test the contact form
    '''

    def test_valid(self):
        company = create_vendor_company()
        form = VendorForm(data={'company': company.pk, 'first_name': 'Ann',
                                  'last_name': 'Lee', 'email': 'ann@example.com'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_company_required(self):
        form = VendorForm(data={'first_name': 'Ann', 'last_name': 'Lee'})
        self.assertFalse(form.is_valid())
        self.assertIn('company', form.errors)

    def test_invalid_email(self):
        company = create_vendor_company()
        form = VendorForm(data={'company': company.pk, 'first_name': 'A',
                                  'last_name': 'B', 'email': 'nope'})
        self.assertFalse(form.is_valid())
