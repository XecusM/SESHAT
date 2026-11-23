from django.test import SimpleTestCase
from django.urls import reverse, resolve

from stock.views import moves as views


class MoveUrlsTest(SimpleTestCase):
    '''
    Test the move urls
    '''

    def test_urls(self):
        cases = [
            ('stock:NewItemMove', views.NewItemMove),
            ('stock:ItemMovesList', views.ItemMovesList),
            ('stock:NewItemTransfer', views.NewItemTransfer),
        ]
        for name, view in cases:
            match = resolve(reverse(name, kwargs={'pk': 1}))
            self.assertEqual(match.func.view_class, view, name)
