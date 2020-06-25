from django.test import TestCase
from django.urls import reverse, resolve

from customer import views


class CustomerUrlsTest(TestCase):
    '''
    Test all urls in the customer applciation
    '''
    def test_new_company_resolved(self):
        '''
        Test new company url
        '''
        url = reverse('customer:company_new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateCompany)

    def test_edit_company_resolved(self):
        '''
        Test edit company url
        '''
        url = reverse('customer:company_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditCompany)

    def test_company_details_resolved(self):
        '''
        Test company details url
        '''
        url = reverse('customer:company_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CompanyDetails)

    def test_companies_list_resolved(self):
        '''
        Test list companies url
        '''
        url = reverse('customer:companies_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CompaniesList)

    def test_delete_company_resolved(self):
        '''
        Test delete company url
        '''
        url = reverse('customer:company_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.company_delete)

    def test_new_customer_resolved(self):
        '''
        Test new customer url
        '''
        url = reverse('customer:customer_new', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateCustomer)

    def test_edit_customer_resolved(self):
        '''
        Test edit customer url
        '''
        url = reverse('customer:customer_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditCustomer)

    def test_customer_details_resolved(self):
        '''
        Test customer details url
        '''
        url = reverse('customer:customer_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CustomerDetails)

    def test_customers_list_resolved(self):
        '''
        Test list customers url
        '''
        url = reverse('customer:customers_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CustomersList)

    def test_delete_customer_resolved(self):
        '''
        Test delete customer url
        '''
        url = reverse('customer:customer_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.customer_delete)
