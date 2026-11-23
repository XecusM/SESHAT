from django.test import SimpleTestCase
from django.urls import reverse, resolve

from customer import views


class CustomerUrlsTest(SimpleTestCase):
    '''
    Test the customer urls
    '''

    def test_urls(self):
        cases = [
            ('customer:NewCompany', views.NewCompany, None),
            ('customer:EditCompany', views.EditCompany, {'pk': 1}),
            ('customer:CompanyDetails', views.CompanyDetails, {'pk': 1}),
            ('customer:CompaniesList', views.CompaniesList, None),
            ('customer:DeleteCompany', views.delete_company, {'pk': 1}),
            ('customer:NewCustomer', views.NewCustomer, None),
            ('customer:EditCustomer', views.EditCustomer, {'pk': 1}),
            ('customer:CustomerDetails', views.CustomerDetails, {'pk': 1}),
            ('customer:CustomersList', views.CustomersList, None),
            ('customer:DeleteCustomer', views.delete_customer, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            match = resolve(reverse(name, kwargs=kwargs))
            self.assertEqual(getattr(match.func, 'view_class', match.func), view, name)
