from django.test import TestCase
from django.urls import reverse

from seshat.testing import (
                        create_user, create_superuser, create_stock,
                        add_quantity, create_assembly, )
from stock.models import ItemMove, ItemTransfer, SubLocation


class MoveViewsTest(TestCase):
    '''
    Test the move and transfer views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())
        self.item = create_stock()
        add_quantity(self.item, 5)

    def test_new_move(self):
        response = self.client.post(
                    reverse('stock:NewItemMove', kwargs={'pk': self.item.pk}),
                    {'type': 'A', 'location': self.item.location.pk,
                     'quantity': 3, 'note': 'found'})
        self.assertRedirects(response, reverse('stock:ItemMovesList', kwargs={'pk': self.item.pk}))
        self.assertEqual(self.item.quantity, 8)
        move = ItemMove.objects.latest('id')
        self.assertEqual(move.get_activities().count(), 1)

    def test_new_move_too_much(self):
        response = self.client.post(
                    reverse('stock:NewItemMove', kwargs={'pk': self.item.pk}),
                    {'type': 'R', 'location': self.item.location.pk,
                     'quantity': 30, 'note': 'lost'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.item.quantity, 5)

    def test_assembly_cannot_be_moved(self):
        kit = create_assembly(components=[(self.item, 1)])
        for name in ['stock:NewItemMove', 'stock:NewItemTransfer']:
            self.assertEqual(self.client.get(reverse(name, kwargs={'pk': kit.pk})).status_code, 403)

    def test_transfer(self):
        other = SubLocation.objects.create(location=self.item.location.location, name='B')
        response = self.client.post(
                    reverse('stock:NewItemTransfer', kwargs={'pk': self.item.pk}),
                    {'old_location': self.item.location.pk,
                     'new_location': other.pk, 'quantity': 2})
        self.assertRedirects(response, reverse('stock:ItemMovesList', kwargs={'pk': self.item.pk}))
        self.assertEqual(ItemTransfer.objects.count(), 1)
        self.assertEqual(self.item.get_quantity(other), 2)

    def test_moves_list(self):
        response = self.client.get(reverse('stock:ItemMovesList', kwargs={'pk': self.item.pk}))
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['locations_list'][0]['quantity'], 5)

    def test_missing_item(self):
        self.assertEqual(self.client.get(
                reverse('stock:ItemMovesList', kwargs={'pk': 999})).status_code, 404)

    def test_permissions(self):
        self.client.force_login(create_user(permissions=['stock.view_item']))
        self.assertEqual(self.client.get(
                reverse('stock:ItemMovesList', kwargs={'pk': self.item.pk})).status_code, 200)
        for name in ['stock:NewItemMove', 'stock:NewItemTransfer']:
            self.assertEqual(self.client.get(
                    reverse(name, kwargs={'pk': self.item.pk})).status_code, 403)
