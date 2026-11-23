from django.test import TestCase

from stock.forms import CategoryForm
from stock.models import Category


class CategoryFormTest(TestCase):
    '''
    Test the category form
    '''

    def test_valid(self):
        form = CategoryForm(data={'name': 'paint'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().name, 'Paint')

    def test_required(self):
        self.assertFalse(CategoryForm(data={'name': ''}).is_valid())

    def test_duplicate(self):
        Category.objects.create(name='Paint')
        self.assertFalse(CategoryForm(data={'name': 'Paint'}).is_valid())
