from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from purchase.models import PurchaseOrder, PurchaseItem
from seshat.testing import create_stock, create_vendor_company
from stock.models import ItemMove


class PurchaseOrderModelTest(TestCase):
    '''
    Test the purchase order model
    '''

    def setUp(self):
        self.company = create_vendor_company('Parts Ltd')
        self.bolt = create_stock(code='BOLT')
        self.nut = create_stock(code='NUT')
        self.order = PurchaseOrder.objects.create(company=self.company)

    def test_str_and_url(self):
        self.assertEqual(str(self.order), f'{self.order.id}-Parts Ltd')
        self.assertTrue(self.order.get_absolute_url().endswith(f'/order/{self.order.pk}/'))

    def test_invoice_details_together(self):
        self.order.invoice = 'INV-1'
        with self.assertRaises(ValidationError):
            self.order.clean()
        self.order.invoice_date = '2026-01-01'
        self.order.clean()

    def test_set_items_adds_stock(self):
        self.order.set_items([
            {'item': self.bolt, 'quantity': 10, 'price': Decimal('1.50'), 'note': 'box'},
            {'item': self.nut, 'quantity': 4, 'price': Decimal('0.25')},
        ])
        self.assertEqual(self.bolt.quantity, 10)
        self.assertEqual(self.nut.quantity, 4)
        self.assertEqual(self.order.total_price, Decimal('16.00'))
        line = self.order.get_items().first()
        self.assertEqual(line.quantity, 10)
        self.assertEqual(line.total_price, Decimal('15.00'))
        self.assertEqual(line.item.related_to, ItemMove.PURCHASE)
        self.assertEqual(str(line), f'{self.order.id}-BOLT')

    def test_set_items_updates_in_place(self):
        self.order.set_items([{'item': self.bolt, 'quantity': 10, 'price': 1},
                              {'item': self.nut, 'quantity': 5, 'price': 1}])
        self.order.set_items([{'item': self.nut, 'quantity': 2, 'price': 3}])
        self.assertEqual(self.bolt.quantity, 0)
        self.assertEqual(self.nut.quantity, 2)
        self.assertEqual(PurchaseItem.objects.count(), 1)
        self.assertEqual(ItemMove.objects.count(), 1)

    def test_reduce_refused_when_stock_used(self):
        self.order.set_items([{'item': self.bolt, 'quantity': 10, 'price': 1}])
        ItemMove.objects.create(item=self.bolt, location=self.bolt.location,
                                type=ItemMove.REMOVE, quantity=8)
        with self.assertRaises(ValidationError):
            self.order.set_items([{'item': self.bolt, 'quantity': 5, 'price': 1}])
        self.assertEqual(self.bolt.quantity, 2)

    def test_delete_removes_lines_and_stock(self):
        self.order.set_items([{'item': self.bolt, 'quantity': 3, 'price': 1}])
        self.order.delete()
        self.assertEqual(self.bolt.quantity, 0)
        self.assertFalse(PurchaseItem.objects.exists())
        self.assertFalse(ItemMove.objects.exists())

    def test_delete_refused_when_stock_used(self):
        self.order.set_items([{'item': self.bolt, 'quantity': 3, 'price': 1}])
        ItemMove.objects.create(item=self.bolt, location=self.bolt.location,
                                type=ItemMove.REMOVE, quantity=1)
        with self.assertRaises(ValidationError):
            self.order.delete()
        self.assertTrue(PurchaseOrder.objects.filter(pk=self.order.pk).exists())
