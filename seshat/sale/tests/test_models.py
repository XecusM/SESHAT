from django.test import TestCase

from django.contrib.auth import get_user_model

from stock import models as stock_models
from customer import models as customers_models
from sale import models as sales_models


class SaleModelsTests(TestCase):
    '''
    Test all models in sale application
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
                                    name='New location')

        self.sub_location = stock_models.SubLocation.objects.create(
                                    location=self.location,
                                    name='new sublocation')

        self.item1 = stock_models.Item.objects.create(
                                    code='code',
                                    category=self.category,
                                    location=self.sub_location,
                                    price=20)

        self.item2 = stock_models.Item.objects.create(
                                    code='second code',
                                    category=self.category,
                                    location=self.sub_location,
                                    price=20)

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

        self.company = customers_models.CustomerCompany.objects.create(
                                                    name='New Company')

    def test_order_create(self):
        '''
        Test creating a new order with minimum values
        '''
        sales_models.SaleOrder.objects.create(company=self.company)

        self.assertEqual(sales_models.SaleOrder.objects.all().count(), 1)

    def test_order_edited(self):
        '''
        Test edited method in Order model
        '''
        order = sales_models.SaleOrder.objects.create(company=self.company)

        order.edited(self.user)

        self.assertEqual(order.edited_by, self.user)

    def test_sale_items_create(self):
        '''
        Test creating a new ourchase items with minimum values
        '''
        order = sales_models.SaleOrder.objects.create(company=self.company)

        sales_models.SaleItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        self.assertEqual(
                    sales_models.SaleItems.objects.all().count(), 1)

    def test_sale_items_edited(self):
        '''
        Test edited method in SaleItems model
        '''
        order = sales_models.SaleOrder.objects.create(company=self.company)

        sale = sales_models.SaleItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        sale.edited(self.user)

        self.assertEqual(sale.edited_by, self.user)

    def test_sale_items_total_price(self):
        '''
        Test total_price property in SaleItems model
        '''
        order = sales_models.SaleOrder.objects.create(company=self.company)

        sale = sales_models.SaleItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        self.assertEqual(
                        sale.total_price,
                        sale.price * self.item1_move.quantity)

    def test_order_total_price(self):
        '''
        Test total_price property in Order model
        '''
        order = sales_models.SaleOrder.objects.create(company=self.company)

        sale1 = sales_models.SaleItems.objects.create(
                                        order=order,
                                        item=self.item1_move,
                                        price=50)

        sale2 = sales_models.SaleItems.objects.create(
                                        order=order,
                                        item=self.item2_move,
                                        price=20)

        order.refresh_from_db()

        self.assertEqual(
                        order.total_price,
                        sale1.price * self.item1_move.quantity \
                        + sale2.price * self.item2_move.quantity)
