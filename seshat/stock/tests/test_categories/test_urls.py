from django.test import SimpleTestCase
from django.urls import reverse, resolve

from stock.views import categories as views


class CategoryUrlsTest(SimpleTestCase):
    '''
    Test the category urls
    '''

    def test_urls(self):
        cases = [
            ('stock:NewCategory', views.NewCategory, None),
            ('stock:EditCategory', views.EditCategory, {'pk': 1}),
            ('stock:CategoriesList', views.CategoriesList, None),
            ('stock:CategoryDetails', views.CategoryDetails, {'pk': 1}),
            ('stock:DeleteCategory', views.delete_category, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            match = resolve(reverse(name, kwargs=kwargs))
            self.assertEqual(getattr(match.func, 'view_class', match.func), view, name)
