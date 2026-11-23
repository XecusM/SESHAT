from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from vendor.models import VendorCompany, Vendor
from seshat.testing import create_vendor_company, create_vendor


class CompanyModelTest(TestCase):
    '''
    Test the company model
    '''

    def setUp(self):
        self.company = create_vendor_company('Acme')

    def test_str_and_url(self):
        self.assertEqual(str(self.company), 'Acme')
        self.assertTrue(self.company.get_absolute_url().endswith(f'/company/{self.company.pk}/'))

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            VendorCompany.objects.create(name='Acme')

    def test_clean_blank_unique_values(self):
        self.company.phone = ''
        self.company.tax_code = ''
        self.company.clean()
        self.assertIsNone(self.company.phone)
        self.assertIsNone(self.company.tax_code)

    def test_invalid_phone_and_website(self):
        self.company.phone = 'abc'
        self.company.website = 'not a url'
        with self.assertRaises(ValidationError) as error:
            self.company.full_clean()
        self.assertIn('phone', error.exception.message_dict)
        self.assertIn('website', error.exception.message_dict)

    def test_contacts_and_delete_check(self):
        self.assertTrue(self.company.can_be_deleted())
        create_vendor(company=self.company, first_name='Zed')
        create_vendor(company=self.company, first_name='Amy')
        self.assertEqual([c.first_name for c in self.company.get_vendors()], ['Amy', 'Zed'])
        self.assertFalse(self.company.can_be_deleted())


class ContactModelTest(TestCase):
    '''
    Test the contact model
    '''

    def test_full_name_and_url(self):
        contact = create_vendor(first_name='Ann', last_name='Lee')
        self.assertEqual(contact.full_name, 'Ann Lee')
        self.assertEqual(str(contact), 'Ann Lee')
        self.assertTrue(contact.get_absolute_url().endswith(f'/{contact.pk}/'))

    def test_clean_blank_unique_values(self):
        contact = Vendor(first_name='A', last_name='B', email='', phone='')
        contact.clean()
        self.assertIsNone(contact.email)
        self.assertIsNone(contact.phone)

    def test_unique_email(self):
        company = create_vendor_company()
        create_vendor(company=company, email='a@b.com')
        with self.assertRaises(IntegrityError):
            create_vendor(company=company, email='a@b.com')

    def test_company_protected(self):
        from django.db.models import ProtectedError
        contact = create_vendor()
        with self.assertRaises(ProtectedError):
            contact.company.delete()
