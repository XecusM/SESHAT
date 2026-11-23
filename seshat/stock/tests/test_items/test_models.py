import os
from decimal import Decimal

from django.db.utils import IntegrityError
from django.test import TestCase

from seshat.testing import (
                        TempDirsTestCase, create_stock, add_quantity,
                        create_assembly, image_file, )
from stock.models import Item, AssemblyItem, SubLocation, items as item_models


class ItemModelTest(TestCase):
    '''
    Test the item model
    '''

    def setUp(self):
        self.item = create_stock(code='BOLT', price='2.50', stock_limit=5)

    def test_clean(self):
        item = Item(code=' nut ', barcode='')
        item.clean()
        self.assertEqual(item.code, 'NUT')
        self.assertIsNone(item.barcode)
        self.assertEqual(str(self.item), 'BOLT')

    def test_unique_code(self):
        with self.assertRaises(IntegrityError):
            create_stock(code='BOLT')

    def test_quantity_from_moves(self):
        self.assertEqual(self.item.quantity, 0)
        add_quantity(self.item, 10)
        from stock.models import ItemMove
        ItemMove.objects.create(item=self.item, location=self.item.location,
                                type=ItemMove.REMOVE, quantity=4)
        self.assertEqual(self.item.quantity, 6)
        self.assertEqual(self.item.get_item_moves().count(), 2)

    def test_quantity_by_location(self):
        other = SubLocation.objects.create(location=self.item.location.location, name='B')
        add_quantity(self.item, 3)
        add_quantity(self.item, 5, other)
        self.assertEqual(self.item.get_quantity(other), 5)
        self.assertEqual(self.item.get_quantity(other.id), 5)
        locations = self.item.get_locations()
        self.assertEqual({row['name']: row['quantity'] for row in locations},
                         {'MAIN / B': 5, 'MAIN / SHELF-1': 3})

    def test_low_stock_and_value(self):
        add_quantity(self.item, 5)
        self.assertTrue(self.item.is_low_stock)
        add_quantity(self.item, 1)
        self.assertFalse(self.item.is_low_stock)
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_value, Decimal('15.00'))
        self.item.stock_limit = None
        self.assertFalse(self.item.is_low_stock)

    def test_can_be_deleted(self):
        self.assertTrue(self.item.can_be_deleted())
        add_quantity(self.item, 1)
        self.assertFalse(self.item.can_be_deleted())

    def test_image_path(self):
        self.assertTrue(item_models.get_image_path(self.item, 'x.png').startswith('items/'))


class AssemblyItemTest(TestCase):
    '''
    Test assembled items
    '''

    def setUp(self):
        self.bolt = create_stock(code='BOLT')
        self.nut = create_stock(code='NUT')
        self.kit = create_assembly(components=[(self.bolt, 2), (self.nut, 3)])

    def test_quantity_from_components(self):
        self.assertEqual(self.kit.quantity, 0)
        add_quantity(self.bolt, 10)
        add_quantity(self.nut, 9)
        self.assertEqual(self.kit.quantity, 3)
        self.assertEqual(self.kit.get_quantity(self.kit.location), 3)
        self.assertEqual(self.kit.get_locations(), [])

    def test_without_components(self):
        self.assertEqual(create_assembly(code='EMPTY').quantity, 0)

    def test_components(self):
        components = list(self.kit.get_assembly_items())
        self.assertEqual([c.sub_item for c in components], [self.bolt, self.nut])
        self.assertEqual(str(components[0]), 'KIT1/BOLT')
        add_quantity(self.bolt, 4)
        self.assertEqual(components[0].sub_item_quantity, 4)

    def test_unique_component(self):
        with self.assertRaises(IntegrityError):
            AssemblyItem.objects.create(item=self.kit, sub_item=self.bolt, quantity=1)

    def test_component_can_not_be_deleted(self):
        self.assertFalse(self.bolt.can_be_deleted())


class ItemPhotoTest(TempDirsTestCase):
    '''
    Test the item photo file signals
    '''

    def test_old_photo_removed(self):
        item = create_stock(photo=image_file('a.png'))
        first = item.photo.path
        item.photo = image_file('b.png')
        item.save()
        self.assertFalse(os.path.isfile(first))
        second = item.photo.path
        item.delete()
        self.assertFalse(os.path.isfile(second))
