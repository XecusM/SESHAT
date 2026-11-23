from django.test import SimpleTestCase
from django.urls import reverse, resolve

from sale import views


class OrderUrlsTest(SimpleTestCase):
    '''
    Test the order urls
    '''

    def test_urls(self):
        cases = [
            ('sale:OrdersList', views.OrdersList, None),
            ('sale:NewOrder', views.NewOrder, None),
            ('sale:EditOrder', views.EditOrder, {'pk': 1}),
            ('sale:OrderDetails', views.OrderDetails, {'pk': 1}),
            ('sale:DeleteOrder', views.delete_order, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            match = resolve(reverse(name, kwargs=kwargs))
            self.assertEqual(getattr(match.func, 'view_class', match.func), view, name)
