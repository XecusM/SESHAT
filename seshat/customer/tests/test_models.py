from django.test import TestCase

from django.contrib.auth import get_user_model

from customer import models as customers_models


class CustomerModelsTests(TestCase):
    '''
    Test all models and methods in customer application
    '''
    def test_company_create(self):
        '''
        Test creating a new company with minimum values
        '''
        customers_models.CustomerCompany.objects.create(name='New Company')

        self.assertEqual(customers_models.CustomerCompany.objects.all().count(), 1)

    def test_company_edited(self):
        '''
        Test edited method in Company model
        '''
        user = get_user_model().objects.create_user(
                                                username='Xecus',
                                                password='testpass')
        company = customers_models.CustomerCompany.objects.create(
                                                        name='New Company')

        company.edited(user)

        self.assertEqual(company.edited_by, user)

    def test_customer_create(self):
        '''
        Test creating a new customer with minimum values
        '''
        company = customers_models.CustomerCompany.objects.create(
                                                        name='New Company')

        customers_models.Customer.objects.create(
                                        company=company,
                                        first_name='Mohamed',
                                        last_name='Aboel-fotouh', )

        self.assertEqual(customers_models.Customer.objects.all().count(), 1)

    def test_company_get_customers(self):
        '''
        Test get_customers method in Company model
        '''
        company = customers_models.CustomerCompany.objects.create(
                                                        name='New Company')

        customer = customers_models.Customer.objects.create(
                                            company=company,
                                            first_name='Mohamed',
                                            last_name='Aboel-fotouh', )

        self.assertEqual(company.get_customers()[0], customer)

    def test_customer_edited(self):
        '''
        Test edited method in Customer model
        '''
        user = get_user_model().objects.create_user(
                                                username='Xecus',
                                                password='testpass')
        company = customers_models.CustomerCompany.objects.create(
                                                        name='New Company')
        customer = customers_models.Customer.objects.create(
                                            company=company,
                                            first_name='Mohamed',
                                            last_name='Aboel-fotouh', )
        customer.edited(user)

        self.assertEqual(customer.edited_by, user)

    def test_customer_full_name(self):
        '''
        Test full_name method in Customer model
        '''
        company = customers_models.CustomerCompany.objects.create(
                                                        name='New Company')
        customer = customers_models.Customer.objects.create(
                                            company=company,
                                            first_name='Mohamed',
                                            last_name='Aboel-fotouh', )

        self.assertEqual(
                        customer.full_name,
                        f"{customer.first_name} {customer.last_name}")
