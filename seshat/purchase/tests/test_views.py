from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from purchase import models, views
from vendor import models as vendors_models
from stock import models as stock_models


class PurchaseViewsTests(TestCase):
    '''
    Test all views for purchase application
    '''
    def setUp(self):
        '''
        Intiate tests
        '''
        self.user = get_user_model().objects.create_user(
                                                username='user',
                                                password='testpassword')

        self.company = vendors_models.VendorCompany.objects.create(
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
        self.move = stock_models.ItemMove.objects.create(
                                    item=self.item,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    location=self.sub_location,
                                    quantity=5)

        self.order = models.PurchaseOrder.objects.create(company=self.company)

        self.purchase_item = models.PurchaseItems.objects.create(
                                    order=self.order,
                                    item=self.move,
                                    price=50)

        self.order_new_url = reverse('purchase:order_new')
        self.order_edit_url = reverse(
                                    'purchase:order_edit',
                                    kwargs={'pk': self.order.id})
        self.order_details_url = reverse(
                                    'purchase:order_details',
                                    kwargs={'pk': self.order.id})
        self.orders_list_url = reverse('purchase:orders_list')
        self.order_delete_url = reverse(
                                    'purchase:order_delete',
                                    kwargs={'pk': self.order.id})

    def test_new_order_get(self):
        '''
        Test get url for creating new order
        '''
        content_type = ContentType.objects.get_for_model(models.PurchaseOrder)
        permission = Permission.objects.get(
                                    codename='add_purchaseorder',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.order_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'purchase/order_new.html')

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
        content_type = ContentType.objects.get_for_model(models.PurchaseOrder)
        permission = Permission.objects.get(
                                    codename='add_purchaseorder',
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
        self.assertEquals(models.PurchaseOrder.objects.all().count(), 2)

    def test_edit_order_get(self):
        '''
        Test get url for creating edit order
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.PurchaseOrder)
        permission = Permission.objects.get(
                                    codename='change_purchaseorder',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.order_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'purchase/order_edit.html')

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
                                                    models.PurchaseOrder)
        permission = Permission.objects.get(
                                    codename='change_purchaseorder',
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
        self.purchase_item.refresh_from_db()
        self.move.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(
                        self.purchase_item.item.quantity,
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
                                'purchase/order_details.html')

    def test_orders_list_get(self):
        '''
        Test get url for orders list
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.orders_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'purchase/orders_list.html')

    def test_order_delete_get(self):
        '''
        Test get url for order delete
        '''
        content_type = ContentType.objects.get_for_model(models.PurchaseOrder)
        permission = Permission.objects.get(
                                    codename='delete_purchaseorder',
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
                                                    models.PurchaseOrder)
        permission = Permission.objects.get(
                                    codename='delete_purchaseorder',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        self.assertEqual(models.PurchaseOrder.objects.all().count(), 1)

        response = self.client.post(self.order_delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.PurchaseOrder.objects.all().count(), 0)
