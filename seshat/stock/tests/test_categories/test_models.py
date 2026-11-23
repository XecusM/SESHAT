from django.db.utils import IntegrityError
from django.test import TestCase

from seshat.testing import create_stock
from stock.models import Category


class CategoryModelTest(TestCase):
    '''
    Test the category model
    '''

    def test_clean_capitalizes(self):
        category = Category(name='  power tools ')
        category.clean()
        self.assertEqual(category.name, 'Power tools')
        self.assertEqual(str(category), 'Power tools')

    def test_unique_name(self):
        Category.objects.create(name='Tools')
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Tools')

    def test_items_and_can_be_deleted(self):
        category = Category.objects.create(name='Empty')
        self.assertTrue(category.can_be_deleted())
        item = create_stock(code='B2', category=category)
        create_stock(code='A1', category=category)
        self.assertEqual([i.code for i in category.get_items()], ['A1', 'B2'])
        self.assertFalse(category.can_be_deleted())
        self.assertEqual(item.category, category)

    def test_ordering(self):
        Category.objects.create(name='Zinc')
        Category.objects.create(name='Alu')
        self.assertEqual([c.name for c in Category.objects.all()], ['Alu', 'Zinc'])
