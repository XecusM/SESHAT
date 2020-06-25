from django.test import TestCase
from django.contrib.auth import get_user_model

from customer import forms, models


class CustomerFormsTests(TestCase):
    '''
    Test all forms in customer application
    '''
    def test_company_form_fields(self):
        '''
        Test company form fields
        '''
        expected = [
                    'name', 'desciption', 'phone',
                    'website', 'taxs_code']

        actual = list(forms.CompanyForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_company_form_valid_data(self):
        '''
        Test valid form for company form
        '''
        form = forms.CompanyForm(data={'name': 'another_user', })

        self.assertTrue(form.is_valid())

    def test_company_form_invalid_data(self):
        '''
        Test invalid form for company form
        '''
        form = forms.CompanyForm(data={'name': '', })

        self.assertFalse(form.is_valid())

    def test_customer_form_fields(self):
        '''
        Test customer form fields
        '''
        expected = [
                    'company', 'first_name', 'last_name', 'email',
                    'phone', 'department', 'job'
            ]

        actual = list(forms.CustomerForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_customer_form_valid_data(self):
        '''
        Test valid form for customer form
        '''
        company = models.CustomerCompany.objects.create(name='New Company')

        form = forms.CustomerForm(data={
                                    'company': company.id,
                                    'first_name': 'Mohamed',
                                    'last_name': 'Aboel-fotouh'
                                })

        self.assertTrue(form.is_valid())

    def test_customer_form_invalid_data(self):
        '''
        Test invalid form for customer form
        '''
        company = models.CustomerCompany.objects.create(name='New Company')

        form_company = forms.CustomerForm(data={
                                    'company': '',
                                    'first_name': 'Mohamed',
                                    'last_name': 'Aboel-fotouh'
                                })

        form_first_name = forms.CustomerForm(data={
                                    'company': company.id,
                                    'first_name': '',
                                    'last_name': 'Aboel-fotouh'
                                })

        form_last_name = forms.CustomerForm(data={
                                    'company': company.id,
                                    'first_name': 'Mohamed',
                                    'last_name': ''
                                })

        self.assertFalse(form_company.is_valid())
        self.assertFalse(form_first_name.is_valid())
        self.assertFalse(form_last_name.is_valid())
