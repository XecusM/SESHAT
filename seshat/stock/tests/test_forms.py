from django.test import TestCase
from django.contrib.auth import get_user_model

from stock import forms, models


class StockFormsTests(TestCase):
    '''
    Test all forms in stock application
    '''
    def setUp(self):
        '''
        initiate all tests
        '''
        self.category = models.Category.objects.create(name='New category')

        self.location = models.Location.objects.create(
                                name='New location')

        self.sub_location = models.SubLocation.objects.create(
                                location=self.location,
                                name='new sublocation')

        self.item = models.Item.objects.create(
                                code='code',
                                category=self.category,
                                location=self.sub_location,
                                price=50)

        self.assembled_item = models.Item.objects.create(
                                code='assembly code',
                                category=self.category,
                                location=self.sub_location,
                                price=50,
                                is_assembly=True)

        self.assembly_item = models.AssemblyItem.objects.create(
                                item=self.assembled_item,
                                sub_item=self.item,
                                quantity=5)

        self.item_move = models.ItemMove.objects.create(
                                item=self.item,
                                location=self.sub_location,
                                type=models.ItemMove.ADD,
                                related_to=models.ItemMove.PURCHASE,
                                quantity=20)

        self.assembled_item_move = models.ItemMove.objects.create(
                                item=self.assembled_item,
                                location=self.sub_location,
                                type=models.ItemMove.REMOVE,
                                related_to=models.ItemMove.SELL,
                                quantity=1)

        self.sub_item_move = models.ItemMove.objects.create(
                                item=self.assembly_item.sub_item,
                                location=self.sub_location,
                                type=models.ItemMove.REMOVE,
                                related_to=models.ItemMove.ASSEMBLY,
                                quantity=self.assembled_item_move.quantity \
                                        * self.assembly_item.quantity
        )

    def test_category_form_fields(self):
        '''
        Test category form fields
        '''
        expected = ['name', ]

        actual = list(forms.CategoryFrom().fields)
        self.assertSequenceEqual(expected, actual)

    def test_category_form_valid_data(self):
        '''
        Test valid form for category form
        '''
        form = forms.CategoryFrom(data={'name': 'another_category', })

        self.assertTrue(form.is_valid())

    def test_category_form_invalid_data(self):
        '''
        Test invalid form for category form
        '''
        form = forms.CategoryFrom(data={'name': '', })

        self.assertFalse(form.is_valid())

    def test_item_form_fields(self):
        '''
        Test item form fields
        '''
        expected = [
                    'code', 'desciption', 'barcode', 'stock_limit',
                    'price', 'location', 'category', 'is_active',
                    'photo', 'x', 'y', 'width', 'height'
        ]
        actual = list(forms.ItemForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_item_form_valid_data(self):
        '''
        Test valid form for item form
        '''
        form = forms.ItemForm(data={
                                    'code': 'code2',
                                    'category': self.category.id,
                                    'location': self.sub_location.id,
                                    'price': 50
                                })

        self.assertTrue(form.is_valid())

    def test_item_form_invalid_data(self):
        '''
        Test invalid form for item form
        '''
        form_code = forms.ItemForm(data={
                                    'code': 'not any code',
                                    'category': self.category.id,
                                    'location': self.sub_location.id,
                                    'price': 50
                                })

        form_category = forms.ItemForm(data={
                                    'code': 'code2',
                                    'category': '',
                                    'location': self.sub_location.id,
                                    'price': 50
                                })

        self.assertFalse(form_code.is_valid())
        self.assertFalse(form_category.is_valid())

    def test_assembly_item_form_fields(self):
        '''
        Test assembled item form fields
        '''
        expected = [
                    'item', 'sub_item', 'quantity'
        ]

        actual = list(forms.AssemblyItemForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_assembly_item_form_valid_data(self):
        '''
        Test valid form for assembled item form
        '''
        form = forms.AssemblyItemForm(data={
                                    'item': self.assembled_item.id,
                                    'sub_item': self.item.id,
                                    'quantity': 10
                                })

        self.assertTrue(form.is_valid())

    def test_assembly_item_form_invalid_data(self):
        '''
        Test invalid form for assembled item form
        '''
        form_item = forms.AssemblyItemForm(data={
                                    'item': '',
                                    'sub_item': self.item.id,
                                    'quantity': 10
                                })

        form_sub_item = forms.AssemblyItemForm(data={
                                    'item': self.assembled_item.id,
                                    'sub_item': '',
                                    'quantity': 10
                                })

        form_quantity = forms.AssemblyItemForm(data={
                                    'item': self.assembled_item.id,
                                    'sub_item': self.item.id,
                                    'quantity': ''
                                })

        self.assertFalse(form_item.is_valid())
        self.assertFalse(form_sub_item.is_valid())
        self.assertFalse(form_quantity.is_valid())

    def test_location_form_fields(self):
        '''
        Test location form fields
        '''
        expected = ['name', ]

        actual = list(forms.LocationForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_location_form_valid_data(self):
        '''
        Test valid form for location form
        '''
        form = forms.LocationForm(data={'name': 'another_location', })

        self.assertTrue(form.is_valid())

    def test_location_form_invalid_data(self):
        '''
        Test invalid form for location form
        '''
        form = forms.LocationForm(data={'name': '', })

        self.assertFalse(form.is_valid())

    def test_sublocation_form_fields(self):
        '''
        Test sublocation form fields
        '''
        expected = ['location', 'name', ]

        actual = list(forms.SubLocationForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_sublocation_form_valid_data(self):
        '''
        Test valid form for sublocation form
        '''
        form = forms.SubLocationForm(data={
                                    'location': self.location.id,
                                    'name': 'another sublocation',
                                })

        self.assertTrue(form.is_valid())

    def test_sublocation_form_invalid_data(self):
        '''
        Test invalid form for sublocation form
        '''
        form_location = forms.SubLocationForm(data={
                                    'location': '',
                                    'name': 'another sublocation',
                                })

        form_name = forms.SubLocationForm(data={
                                    'location': self.location.id,
                                    'name': '',
                                })

        self.assertFalse(form_location.is_valid())
        self.assertFalse(form_name.is_valid())

    def test_item_move_form_fields(self):
        '''
        Test item move form fields
        '''
        expected = [
                    'item', 'type', 'location', 'quantity', 'note'
        ]

        actual = list(forms.ItemMoveForm().fields)
        self.assertSequenceEqual(expected, actual)

    def test_item_move_form_valid_data(self):
        '''
        Test valid form for item move form
        '''
        form = forms.ItemMoveForm(data={
                                    'item': self.item.id,
                                    'location': self.sub_location.id,
                                    'type': models.ItemMove.ADD,
                                    'quantity': 10
                                })

        self.assertTrue(form.is_valid())

    def test_item_move_form_invalid_data(self):
        '''
        Test invalid form for item move form
        '''
        form_item = forms.ItemMoveForm(data={
                                    'item': '',
                                    'location': self.sub_location.id,
                                    'type': models.ItemMove.ADD,
                                    'quantity': 10
                                })

        form_location = forms.ItemMoveForm(data={
                                    'item': self.item.id,
                                    'location': '',
                                    'type': models.ItemMove.ADD,
                                    'quantity': 10
                                })

        form_type = forms.ItemMoveForm(data={
                                    'item': self.item.id,
                                    'location': self.sub_location.id,
                                    'type': '',
                                    'quantity': 10
                                })

        form_quantity = forms.ItemMoveForm(data={
                                    'item': self.item.id,
                                    'location': self.sub_location.id,
                                    'type': models.ItemMove.ADD,
                                    'quantity': ''
                                })

        self.assertFalse(form_item.is_valid())
        self.assertFalse(form_location.is_valid())
        self.assertFalse(form_type.is_valid())
        self.assertFalse(form_quantity.is_valid())
