from django.test import TestCase

from seshat.testing import TempDirsTestCase, create_stock, image_file
from stock.forms import ItemForm, AssemblyItemFormSet
from stock.models import Category, SubLocation, Location, Item


class ItemFormTest(TempDirsTestCase):
    '''
    Test the item form
    '''

    def setUp(self):
        self.category = Category.objects.create(name='General')
        self.location = SubLocation.objects.create(
                                location=Location.objects.create(name='MAIN'), name='A')

    def data(self, **extra):
        data = {'code': 'new1', 'description': 'New', 'category': self.category.pk,
                'location': self.location.pk, 'price': '3.00', 'is_active': 'on'}
        data.update(extra)
        return data

    def test_valid(self):
        form = ItemForm(data=self.data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().code, 'NEW1')

    def test_negative_price(self):
        self.assertFalse(ItemForm(data=self.data(price='-1')).is_valid())

    def test_photo_resized(self):
        from PIL import Image
        form = ItemForm(data=self.data(x=0, y=0, width=500, height=500),
                        files={'photo': image_file(size=(700, 700))})
        self.assertTrue(form.is_valid(), form.errors)
        item = form.save()
        with Image.open(item.photo.path) as image:
            self.assertEqual(image.size, (500, 500))

    def test_assembly_flag_locked_on_edit(self):
        item = create_stock()
        self.assertTrue(ItemForm(instance=item).fields['is_assembly'].disabled)
        self.assertFalse(ItemForm().fields['is_assembly'].disabled)


class AssemblyFormSetTest(TestCase):
    '''
    Test the components formset
    '''

    def setUp(self):
        self.bolt = create_stock(code='BOLT')
        self.nut = create_stock(code='NUT')

    def formset(self, rows, instance=None):
        data = {'components-TOTAL_FORMS': len(rows), 'components-INITIAL_FORMS': 0}
        for index, (item, quantity) in enumerate(rows):
            data[f'components-{index}-sub_item'] = item.pk if item else ''
            data[f'components-{index}-quantity'] = quantity
        return AssemblyItemFormSet(data, instance=instance or Item(), prefix='components')

    def test_valid(self):
        self.assertTrue(self.formset([(self.bolt, 2), (self.nut, 1)]).is_valid())

    def test_duplicate_component(self):
        formset = self.formset([(self.bolt, 2), (self.bolt, 1)])
        self.assertFalse(formset.is_valid())
        self.assertIn('duplicate', str(formset.non_form_errors()).lower())

    def test_needs_component(self):
        formset = self.formset([])
        self.assertFalse(formset.is_valid())

    def test_assembled_items_not_offered(self):
        kit = create_stock(code='KIT', is_assembly=True)
        formset = self.formset([(kit, 1)])
        self.assertFalse(formset.is_valid())

    def test_zero_quantity(self):
        self.assertFalse(self.formset([(self.bolt, 0)]).is_valid())
