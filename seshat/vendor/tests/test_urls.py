from django.test import TestCase
from django.urls import reverse, resolve

from vendor import views


class VendorUrlsTest(TestCase):
    '''
    Test all urls in the vendor applciation
    '''
    def test_new_company_resolved(self):
        '''
        Test new company url
        '''
        url = reverse('vendor:company_new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateCompany)

    def test_edit_company_resolved(self):
        '''
        Test edit company url
        '''
        url = reverse('vendor:company_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditCompany)

    def test_company_details_resolved(self):
        '''
        Test company details url
        '''
        url = reverse('vendor:company_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CompanyDetails)

    def test_companies_list_resolved(self):
        '''
        Test list companies url
        '''
        url = reverse('vendor:companies_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CompaniesList)

    def test_delete_company_resolved(self):
        '''
        Test delete company url
        '''
        url = reverse('vendor:company_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.company_delete)

    def test_new_vendor_resolved(self):
        '''
        Test new vendor url
        '''
        url = reverse('vendor:vendor_new', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateVendor)

    def test_edit_vendor_resolved(self):
        '''
        Test edit vendor url
        '''
        url = reverse('vendor:vendor_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditVendor)

    def test_vendor_details_resolved(self):
        '''
        Test vendor details url
        '''
        url = reverse('vendor:vendor_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.VendorDetails)

    def test_vendors_list_resolved(self):
        '''
        Test list vendors url
        '''
        url = reverse('vendor:vendors_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.VendorsList)

    def test_delete_vendor_resolved(self):
        '''
        Test delete vendor url
        '''
        url = reverse('vendor:vendor_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.vendor_delete)
