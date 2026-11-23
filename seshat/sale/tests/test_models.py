from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from sale.models import SaleOrder, SaleItem
from seshat.testing import (
                        create_stock, create_customer_company,
                        add_quantity, create_assembly, )
from stock.models import ItemMove


class SaleOrderModelTest(TestCase):
    '''
    Test the sale order model
    '''

    def setUp(self):
        self.company = create_customer_company('Buyer')
        self.bolt = create_stock(code='BOLT')
        self.nut = create_stock(code='NUT')
        add_quantity(self.bolt, 10)
        add_quantity(self.nut, 10)
        self.order = SaleOrder.objects.create(company=self.company)

    def test_str_and_url(self):
        self.assertEqual(str(self.order), f'{self.order.id}-Buyer')
        self.assertTrue(self.order.get_absolute_url().endswith(f'/order/{self.order.pk}/'))

    def test_invoice_details_together(self):
        self.order.invoice_date = '2026-01-01'
        with self.assertRaises(ValidationError):
            self.order.clean()

    def test_set_items_removes_stock(self):
        self.order.set_items([{'item': self.bolt, 'quantity': 4, 'price': Decimal('3')},
                              {'item': self.nut, 'quantity': 1, 'price': Decimal('2')}])
        self.assertEqual(self.bolt.quantity, 6)
        self.assertEqual(self.order.total_price, Decimal('14'))
        line = self.order.get_items().first()
        self.assertEqual(line.item.type, ItemMove.REMOVE)
        self.assertEqual(line.item.related_to, ItemMove.SELL)
        self.assertEqual(str(line), f'{self.order.id}-BOLT')

    def test_can_not_sell_more_than_stock(self):
        with self.assertRaises(ValidationError):
            self.order.set_items([{'item': self.bolt, 'quantity': 11, 'price': 1}])
        self.assertEqual(self.bolt.quantity, 10)

    def test_edit_counts_own_quantity(self):
        self.order.set_items([{'item': self.bolt, 'quantity': 10, 'price': 1}])
        self.order.set_items([{'item': self.bolt, 'quantity': 10, 'price': 2}])
        self.assertEqual(self.bolt.quantity, 0)
        self.order.set_items([{'item': self.bolt, 'quantity': 4, 'price': 2}])
        self.assertEqual(self.bolt.quantity, 6)

    def test_sell_assembled_item(self):
        kit = create_assembly(components=[(self.bolt, 2), (self.nut, 1)])
        self.order.set_items([{'item': kit, 'quantity': 3, 'price': 9}])
        self.assertEqual(self.bolt.quantity, 4)
        self.assertEqual(self.nut.quantity, 7)
        self.order.delete()
        self.assertEqual(self.bolt.quantity, 10)
        self.assertFalse(SaleItem.objects.exists())

    def test_delete_returns_stock(self):
        self.order.set_items([{'item': self.bolt, 'quantity': 5, 'price': 1}])
        self.order.delete()
        self.assertEqual(self.bolt.quantity, 10)
        self.assertFalse(SaleOrder.objects.exists())
