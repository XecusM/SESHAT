from django.test import TestCase
from django.urls import reverse, resolve

from sale import views


class SaleUrlsTest(TestCase):
    '''
    Test all urls in the sale applciation
    '''
    def test_new_order_resolved(self):
        '''
        Test new order url
        '''
        url = reverse('sale:order_new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateOrder)

    def test_edit_order_resolved(self):
        '''
        Test edit order url
        '''
        url = reverse('sale:order_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditOrder)

    def test_order_details_resolved(self):
        '''
        Test order details url
        '''
        url = reverse('sale:order_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.OrderDetails)

    def test_orders_list_resolved(self):
        '''
        Test list orders url
        '''
        url = reverse('sale:orders_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.OrdersList)

    def test_delete_order_resolved(self):
        '''
        Test delete order url
        '''
        url = reverse('sale:order_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.order_delete)
