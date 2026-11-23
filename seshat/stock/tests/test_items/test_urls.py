from django.test import SimpleTestCase
from django.urls import reverse, resolve

from stock.views import items as views


class ItemUrlsTest(SimpleTestCase):
    '''
    Test the item urls
    '''

    def test_urls(self):
        cases = [
            ('stock:Index', views.Index, None),
            ('stock:NewItem', views.NewItem, None),
            ('stock:EditItem', views.EditItem, {'pk': 1}),
            ('stock:ItemsList', views.ItemsList, None),
            ('stock:ItemDetails', views.ItemDetails, {'pk': 1}),
            ('stock:DeleteItem', views.delete_item, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            match = resolve(reverse(name, kwargs=kwargs))
            self.assertEqual(getattr(match.func, 'view_class', match.func), view, name)
