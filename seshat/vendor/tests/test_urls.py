from django.test import SimpleTestCase
from django.urls import reverse, resolve

from vendor import views


class VendorUrlsTest(SimpleTestCase):
    '''
    Test the vendor urls
    '''

    def test_urls(self):
        cases = [
            ('vendor:NewCompany', views.NewCompany, None),
            ('vendor:EditCompany', views.EditCompany, {'pk': 1}),
            ('vendor:CompanyDetails', views.CompanyDetails, {'pk': 1}),
            ('vendor:CompaniesList', views.CompaniesList, None),
            ('vendor:DeleteCompany', views.delete_company, {'pk': 1}),
            ('vendor:NewVendor', views.NewVendor, None),
            ('vendor:EditVendor', views.EditVendor, {'pk': 1}),
            ('vendor:VendorDetails', views.VendorDetails, {'pk': 1}),
            ('vendor:VendorsList', views.VendorsList, None),
            ('vendor:DeleteVendor', views.delete_vendor, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            match = resolve(reverse(name, kwargs=kwargs))
            self.assertEqual(getattr(match.func, 'view_class', match.func), view, name)
