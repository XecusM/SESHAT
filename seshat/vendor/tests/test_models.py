from django.test import TestCase

from django.contrib.auth import get_user_model

from vendor import models as vendors_models


class VendorModelsTests(TestCase):
    '''
    Test all models and methods in vendor application
    '''
    def test_company_create(self):
        '''
        Test creating a new company with minimum values
        '''
        vendors_models.VendorCompany.objects.create(name='New Company')

        self.assertEqual(
                    vendors_models.VendorCompany.objects.all().count(), 1)

    def test_company_edited(self):
        '''
        Test edited method in Company model
        '''
        user = get_user_model().objects.create_user(
                                                username='Xecus',
                                                password='testpass')
        compnay = vendors_models.VendorCompany.objects.create(
                                                name='New Company')

        compnay.edited(user)

        self.assertEqual(compnay.edited_by, user)

    def test_vendor_create(self):
        '''
        Test creating a new vendor with minimum values
        '''
        company = vendors_models.VendorCompany.objects.create(
                                                name='New Company')

        vendors_models.Vendor.objects.create(
                                        company=company,
                                        first_name='Mohamed',
                                        last_name='Aboel-fotouh', )

        self.assertEqual(vendors_models.Vendor.objects.all().count(), 1)

    def test_company_get_vendors(self):
        '''
        Test get_vendors method in Company model
        '''
        company = vendors_models.VendorCompany.objects.create(
                                                name='New Company')

        vendor = vendors_models.Vendor.objects.create(
                                            company=company,
                                            first_name='Mohamed',
                                            last_name='Aboel-fotouh', )

        self.assertEqual(company.get_vendors()[0], vendor)

    def test_vendor_edited(self):
        '''
        Test edited method in Vendor model
        '''
        user = get_user_model().objects.create_user(
                                                username='Xecus',
                                                password='testpass')
        company = vendors_models.VendorCompany.objects.create(
                                                name='New Company')
        vendor = vendors_models.Vendor.objects.create(
                                            company=company,
                                            first_name='Mohamed',
                                            last_name='Aboel-fotouh', )
        vendor.edited(user)

        self.assertEqual(vendor.edited_by, user)

    def test_vendor_full_name(self):
        '''
        Test full_name method in Vendor model
        '''
        company = vendors_models.VendorCompany.objects.create(
                                            name='New Company')
        vendor = vendors_models.Vendor.objects.create(
                                            company=company,
                                            first_name='Mohamed',
                                            last_name='Aboel-fotouh', )

        self.assertEqual(
                        vendor.full_name,
                        f"{vendor.first_name} {vendor.last_name}")
