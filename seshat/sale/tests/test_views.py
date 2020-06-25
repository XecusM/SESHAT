from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from sale import models, views
from customer import models as customers_models
from stock import models as stock_models


class SaleViewsTests(TestCase):
    '''
    Test all views for sale application
    '''
    def setUp(self):
        '''
        Intiate tests
        '''
        self.user = get_user_model().objects.create_user(
                                                username='user',
                                                password='testpassword')

        self.company = customers_models.CustomerCompany.objects.create(
                                                name='New Company')

        self.category = stock_models.Category.objects.create(
                                                name='new category')
        self.location = stock_models.Location.objects.create(
                                                name='new location')
        self.sub_location = stock_models.SubLocation.objects.create(
                                                location=self.location,
                                                name='new sub_location')
        self.item = stock_models.Item.objects.create(
                                                code='code',
                                                category=self.category,
                                                location=self.sub_location,
                                                price=50)
        stock_models.ItemMove.objects.create(
                                    item=self.item,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    location=self.sub_location,
                                    quantity=100)

        self.move = stock_models.ItemMove.objects.create(
                                    item=self.item,
                                    type=stock_models.ItemMove.REMOVE,
                                    related_to=stock_models.ItemMove.SELL,
                                    location=self.sub_location,
                                    quantity=5)

        self.order = models.SaleOrder.objects.create(company=self.company)

        self.sale_item = models.SaleItems.objects.create(
                                    order=self.order,
                                    item=self.move,
                                    price=50)

        self.order_new_url = reverse('sale:order_new')
        self.order_edit_url = reverse(
                                    'sale:order_edit',
                                    kwargs={'pk': self.order.id})
        self.order_details_url = reverse(
                                    'sale:order_details',
                                    kwargs={'pk': self.order.id})
        self.orders_list_url = reverse('sale:orders_list')
        self.order_delete_url = reverse(
                                    'sale:order_delete',
                                    kwargs={'pk': self.order.id})

    def test_new_order_get(self):
        '''
        Test get url for creating new order
        '''
        content_type = ContentType.objects.get_for_model(models.SaleOrder)
        permission = Permission.objects.get(
                                    codename='add_saleorder',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.order_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'sale/order_new.html')

    def test_new_order_permission(self):
        '''
        Test permissions for creating new order
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.order_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_order_post(self):
        '''
        Test post url for creating new order
        '''
        content_type = ContentType.objects.get_for_model(models.SaleOrder)
        permission = Permission.objects.get(
                                    codename='add_saleorder',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'company': self.company.id,
                    'items_count': 1,
                    '1item': self.item.id,
                    '1quantity': 5,
                    '1price': 50,
                    '1note': 'test'
                }

        response = self.client.post(self.order_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.SaleOrder.objects.all().count(), 2)

    def test_edit_order_get(self):
        '''
        Test get url for creating edit order
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.SaleOrder)
        permission = Permission.objects.get(
                                    codename='change_saleorder',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.order_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'sale/order_edit.html')

    def test_edit_order_permission(self):
        '''
        Test permissions for creating edit order
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.order_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_order_post(self):
        '''
        Test post url for creating edit order
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.SaleOrder)
        permission = Permission.objects.get(
                                    codename='change_saleorder',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'company': self.company.id,
                    'items_count': 1,
                    '1item': self.item.id,
                    '1quantity': 10,
                    '1price': 50,
                    '1note': 'test'
                }


        response = self.client.post(self.order_edit_url, data=payload)

        self.order.refresh_from_db()
        self.sale_item.refresh_from_db()
        self.move.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(
                        self.sale_item.item.quantity,
                        payload['1quantity'])

    def test_order_details_get(self):
        '''
        Test get url for order details
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.order_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'sale/order_details.html')

    def test_orders_list_get(self):
        '''
        Test get url for orders list
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.orders_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'sale/orders_list.html')

    def test_order_delete_get(self):
        '''
        Test get url for order delete
        '''
        content_type = ContentType.objects.get_for_model(models.SaleOrder)
        permission = Permission.objects.get(
                                    codename='delete_saleorder',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.order_delete_url)

        self.assertEqual(response.status_code, 404)

    def test_order_delete_permission(self):
        '''
        Test permissions for order delete
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.order_delete_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_order_post(self):
        '''
        Test post url for order delete
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.SaleOrder)
        permission = Permission.objects.get(
                                    codename='delete_saleorder',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        self.assertEqual(models.SaleOrder.objects.all().count(), 1)

        response = self.client.post(self.order_delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.SaleOrder.objects.all().count(), 0)
