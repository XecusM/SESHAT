from django.test import TestCase

from django.contrib.auth import get_user_model

from stock import models as stock_models
from vendor import models as vendors_models
from purchase import models as purchase_models


class PurchaseModelsTests(TestCase):
    '''
    Test all models in purchase application
    '''
    def setUp(self):
        '''
        Initiate all tests
        '''
        self.user = get_user_model().objects.create_user(
                                    username='xecus',
                                    first_name='Mohamed',
                                    last_name='Aboel-fotouh',
                                    password='Testpass123')

        self.category = stock_models.Category.objects.create(
                                    name='New category')

        self.location = stock_models.Location.objects.create(
                                    name='new location')
        self.sub_location = stock_models.SubLocation.objects.create(
                                    location=self.location,
                                    name='new sub_location')

        self.item1 = stock_models.Item.objects.create(
                                    code='code',
                                    category=self.category,
                                    location=self.sub_location,
                                    price=50)

        self.item2 = stock_models.Item.objects.create(
                                    code='second code',
                                    category=self.category,
                                    location=self.sub_location,
                                    price=50)

        self.item1_move = stock_models.ItemMove.objects.create(
                                    item=self.item1,
                                    location=self.sub_location,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    quantity=20)

        self.item2_move = stock_models.ItemMove.objects.create(
                                    item=self.item2,
                                    location=self.sub_location,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    quantity=5)

        self.company = vendors_models.VendorCompany.objects.create(
                                                    name='New Company')

    def test_order_create(self):
        '''
        Test creating a new order with minimum values
        '''
        purchase_models.PurchaseOrder.objects.create(company=self.company)

        self.assertEqual(purchase_models.PurchaseOrder.objects.all().count(), 1)

    def test_order_edited(self):
        '''
        Test edited method in Order model
        '''
        order = purchase_models.PurchaseOrder.objects.create(company=self.company)

        order.edited(self.user)

        self.assertEqual(order.edited_by, self.user)

    def test_purchase_items_create(self):
        '''
        Test creating a new ourchase items with minimum values
        '''
        order = purchase_models.PurchaseOrder.objects.create(company=self.company)

        purchase_models.PurchaseItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        self.assertEqual(
                    purchase_models.PurchaseItems.objects.all().count(), 1)

    def test_purchase_items_edited(self):
        '''
        Test edited method in PurchaseItems model
        '''
        order = purchase_models.PurchaseOrder.objects.create(company=self.company)

        purchase = purchase_models.PurchaseItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        purchase.edited(self.user)

        self.assertEqual(purchase.edited_by, self.user)

    def test_purchase_items_total_price(self):
        '''
        Test total_price property in PurchaseItems model
        '''
        order = purchase_models.PurchaseOrder.objects.create(company=self.company)

        purchase = purchase_models.PurchaseItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        self.assertEqual(
                        purchase.total_price,
                        purchase.price * self.item1_move.quantity)

    def test_order_total_price(self):
        '''
        Test total_price property in Order model
        '''
        order = purchase_models.PurchaseOrder.objects.create(company=self.company)

        purchase1 = purchase_models.PurchaseItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        purchase2 = purchase_models.PurchaseItems.objects.create(
                                        order=order,
                                        item=self.item2_move,
                                        price=20)

        order.refresh_from_db()

        self.assertEqual(
                        order.total_price,
                        purchase1.price * self.item1_move.quantity \
                        + purchase2.price * self.item2_move.quantity)
