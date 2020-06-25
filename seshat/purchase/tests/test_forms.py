from django.test import TestCase

from django.contrib.auth import get_user_model

from stock import models as stock_models
from vendor import models as vendors_models
from purchase import models as purchase_models

from purchase import forms

class PurchaseFormsTests(TestCase):
    '''
    Test all forms in purchase application
    '''
    def setUp(self):
        '''
        Initiate all tests
        '''
        self.category = stock_models.Category.objects.create(
                                        name='New category')

        self.location = stock_models.Location.objects.create(
                                    name='New location')

        self.sub_location = stock_models.SubLocation.objects.create(
                                    location=self.location,
                                    name='new sublocation')

        self.item = stock_models.Item.objects.create(
                                    code='code',
                                    category=self.category,
                                    location=self.sub_location,
                                    price=50)

        self.item_move = stock_models.ItemMove.objects.create(
                                    item=self.item,
                                    location=self.sub_location,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    quantity=20)

        self.company = vendors_models.VendorCompany.objects.create(
                                                    name='New Company')

        self.order = purchase_models.PurchaseOrder.objects.create(
                                                    company=self.company)

    def test_order_form_fields(self):
        '''
        Test order form fields
        '''
        expected = ['company', 'invoice', 'invoice_date', 'note', ]

        actual = list(forms.OrderForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_order_form_valid_data(self):
        '''
        Test valid form for order form
        '''
        form = forms.OrderForm(data={'company': self.company.id, })

        self.assertTrue(form.is_valid())

    def test_order_form_invalid_data(self):
        '''
        Test invalid form for order form
        '''
        form = forms.OrderForm(data={'company': '', })

        self.assertFalse(form.is_valid())
