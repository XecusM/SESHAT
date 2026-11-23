from django.test import TestCase

from seshat.testing import create_stock, add_quantity
from stock.forms import ItemMoveForm, ItemTransferForm
from stock.models import ItemMove, SubLocation


class ItemMoveFormTest(TestCase):
    '''
    Test the custom move form
    '''

    def setUp(self):
        self.item = create_stock()
        add_quantity(self.item, 5)

    def form(self, **data):
        values = {'type': ItemMove.REMOVE, 'location': self.item.location.pk,
                  'quantity': 2, 'note': 'damaged'}
        values.update(data)
        return ItemMoveForm(data=values, item=self.item)

    def test_valid_remove(self):
        form = self.form()
        self.assertTrue(form.is_valid(), form.errors)
        move = form.save()
        self.assertEqual(move.related_to, ItemMove.CUSTOM)
        self.assertEqual(self.item.quantity, 3)

    def test_too_much(self):
        form = self.form(quantity=6)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_note_required(self):
        self.assertFalse(self.form(note='').is_valid())

    def test_zero_quantity(self):
        self.assertFalse(self.form(quantity=0).is_valid())

    def test_default_location(self):
        self.assertEqual(ItemMoveForm(item=self.item).fields['location'].initial,
                         self.item.location_id)


class ItemTransferFormTest(TestCase):
    '''
    Test the transfer form
    '''

    def setUp(self):
        self.item = create_stock()
        self.other = SubLocation.objects.create(location=self.item.location.location, name='B')
        add_quantity(self.item, 5)

    def form(self, **data):
        values = {'old_location': self.item.location.pk, 'new_location': self.other.pk,
                  'quantity': 2}
        values.update(data)
        return ItemTransferForm(data=values, item=self.item)

    def test_valid(self):
        form = self.form()
        self.assertTrue(form.is_valid(), form.errors)
        transfer = form.save()
        self.assertEqual(self.item.get_quantity(self.other), 2)
        self.assertEqual(transfer.old_location, self.item.location)

    def test_only_stocked_locations_to_move_from(self):
        self.assertEqual(list(self.form().fields['old_location'].queryset), [self.item.location])

    def test_same_location(self):
        form = self.form(new_location=self.item.location.pk)
        self.assertFalse(form.is_valid())
        self.assertIn('new_location', form.errors)

    def test_too_much(self):
        form = self.form(quantity=9)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
