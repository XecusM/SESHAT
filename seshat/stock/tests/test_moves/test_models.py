from django.core.exceptions import ValidationError
from django.test import TestCase

from seshat.testing import create_stock, add_quantity, create_assembly
from stock.models import ItemMove, AssemblyMove, ItemTransfer, SubLocation


class ItemMoveModelTest(TestCase):
    '''
    Test the item move model
    '''

    def setUp(self):
        self.item = create_stock()

    def remove(self, quantity, location=None):
        return ItemMove.objects.create(
                    item=self.item, location=location or self.item.location,
                    type=ItemMove.REMOVE, quantity=quantity)

    def test_str_and_signed_quantity(self):
        move = add_quantity(self.item, 5)
        self.assertEqual(move.signed_quantity, 5)
        self.assertEqual(str(move), f'Add-{move.id}')
        self.assertEqual(self.remove(2).signed_quantity, -2)

    def test_negative_stock_refused(self):
        add_quantity(self.item, 2)
        with self.assertRaises(ValidationError):
            self.remove(3)
        self.assertEqual(self.item.quantity, 2)

    def test_negative_stock_per_location(self):
        other = SubLocation.objects.create(location=self.item.location.location, name='B')
        add_quantity(self.item, 5, other)
        with self.assertRaises(ValidationError):
            self.remove(1)

    def test_update_checks_stock(self):
        move = add_quantity(self.item, 10)
        self.remove(8)
        move.quantity = 5
        with self.assertRaises(ValidationError):
            move.save()
        move.quantity = 8
        move.save()
        self.assertEqual(self.item.quantity, 0)

    def test_moving_to_another_location_checks_old_location(self):
        move = add_quantity(self.item, 5)
        self.remove(2)
        move.location = SubLocation.objects.create(location=self.item.location.location, name='B')
        with self.assertRaises(ValidationError):
            move.save()

    def test_delete_add_move_checks_stock(self):
        move = add_quantity(self.item, 5)
        self.remove(1)
        with self.assertRaises(ValidationError):
            move.delete()
        self.remove(4)
        with self.assertRaises(ValidationError):
            move.delete()

    def test_delete_remove_move(self):
        add_quantity(self.item, 5)
        self.remove(3).delete()
        self.assertEqual(self.item.quantity, 5)


class AssemblyMoveTest(TestCase):
    '''
    Moves of an assembled item move its components
    '''

    def setUp(self):
        self.bolt = create_stock(code='BOLT')
        self.nut = create_stock(code='NUT')
        self.kit = create_assembly(components=[(self.bolt, 2), (self.nut, 1)])
        add_quantity(self.bolt, 10)
        add_quantity(self.nut, 10)

    def sell(self, quantity):
        return ItemMove.objects.create(
                    item=self.kit, location=self.kit.location,
                    type=ItemMove.REMOVE, related_to=ItemMove.SELL, quantity=quantity)

    def test_component_moves_created(self):
        move = self.sell(3)
        self.assertEqual(self.bolt.quantity, 4)
        self.assertEqual(self.nut.quantity, 7)
        assembly_move = AssemblyMove.objects.get(assembly_move=move)
        self.assertEqual(assembly_move.item_moves.count(), 2)
        self.assertEqual(str(assembly_move), f'KIT1-{assembly_move.id}')
        self.assertTrue(all(m.related_to == ItemMove.ASSEMBLY
                            for m in assembly_move.item_moves.all()))

    def test_component_moves_updated(self):
        move = self.sell(3)
        move.quantity = 1
        move.save()
        self.assertEqual(self.bolt.quantity, 8)
        self.assertEqual(self.nut.quantity, 9)

    def test_not_enough_components(self):
        with self.assertRaises(ValidationError):
            self.sell(6)
        self.assertEqual(self.bolt.quantity, 10)
        self.assertFalse(ItemMove.objects.filter(item=self.kit).exists())

    def test_delete_restores_components(self):
        move = self.sell(2)
        move.delete()
        self.assertEqual(self.bolt.quantity, 10)
        self.assertEqual(self.nut.quantity, 10)
        self.assertFalse(AssemblyMove.objects.exists())

    def test_assembly_without_components(self):
        empty = create_assembly(code='EMPTY')
        with self.assertRaises(ValidationError):
            ItemMove.objects.create(item=empty, location=empty.location,
                                    type=ItemMove.ADD, quantity=1)


class ItemTransferModelTest(TestCase):
    '''
    Test transfers between sub-locations
    '''

    def setUp(self):
        self.item = create_stock()
        self.other = SubLocation.objects.create(location=self.item.location.location, name='B')
        add_quantity(self.item, 10)

    def test_transfer(self):
        transfer = ItemTransfer.transfer(self.item, self.item.location, self.other, 4, 'move')
        self.assertEqual(transfer.quantity, 4)
        self.assertEqual(self.item.get_quantity(self.other), 4)
        self.assertEqual(self.item.get_quantity(self.item.location), 6)
        self.assertEqual(self.item.quantity, 10)
        self.assertIn('MAIN / B', str(transfer))

    def test_same_location(self):
        with self.assertRaises(ValidationError):
            ItemTransfer.transfer(self.item, self.other, self.other, 1)

    def test_not_enough(self):
        with self.assertRaises(ValidationError):
            ItemTransfer.transfer(self.item, self.item.location, self.other, 11)
        self.assertEqual(ItemMove.objects.count(), 1)
