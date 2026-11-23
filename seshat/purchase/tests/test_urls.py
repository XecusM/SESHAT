from django.test import SimpleTestCase
from django.urls import reverse, resolve

from purchase import views


class OrderUrlsTest(SimpleTestCase):
    '''
    Test the order urls
    '''

    def test_urls(self):
        cases = [
            ('purchase:OrdersList', views.OrdersList, None),
            ('purchase:NewOrder', views.NewOrder, None),
            ('purchase:EditOrder', views.EditOrder, {'pk': 1}),
            ('purchase:OrderDetails', views.OrderDetails, {'pk': 1}),
            ('purchase:DeleteOrder', views.delete_order, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            match = resolve(reverse(name, kwargs=kwargs))
            self.assertEqual(getattr(match.func, 'view_class', match.func), view, name)
