from django.test import TestCase
from django.urls import reverse

from seshat.testing import (
                        TempDirsTestCase, create_user, create_superuser,
                        create_stock, add_quantity, create_assembly, )
from stock.models import Item, AssemblyItem


class StockIndexViewTest(TestCase):
    '''
    Test the stock dashboard
    '''

    def test_dashboard(self):
        item = create_stock(stock_limit=10, price='2')
        add_quantity(item, 4)
        self.client.force_login(create_user(permissions=['stock.view_item']))
        response = self.client.get(reverse('stock:Index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['low_stock_list'], [item])
        self.assertEqual(response.context['stock_value'], 8)
        self.assertEqual(len(response.context['itemmove_list']), 1)

    def test_permission(self):
        self.client.force_login(create_user())
        self.assertEqual(self.client.get(reverse('stock:Index')).status_code, 403)


class ItemViewsTest(TempDirsTestCase):
    '''
    Test the item views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())
        self.item = create_stock(code='BOLT', description='Hex bolt')

    def data(self, **extra):
        data = {'code': 'nut', 'category': self.item.category.pk,
                'location': self.item.location.pk, 'price': '1.50', 'is_active': 'on',
                'components-TOTAL_FORMS': 0, 'components-INITIAL_FORMS': 0}
        data.update(extra)
        return data

    def test_new_item(self):
        response = self.client.post(reverse('stock:NewItem'), self.data())
        item = Item.objects.get(code='NUT')
        self.assertRedirects(response, reverse('stock:ItemDetails', kwargs={'pk': item.pk}))
        self.assertEqual(item.get_activities().count(), 1)

    def test_new_assembly(self):
        data = self.data(code='kit', is_assembly='on', **{
                'components-TOTAL_FORMS': 1,
                'components-0-sub_item': self.item.pk, 'components-0-quantity': 4})
        self.client.post(reverse('stock:NewItem'), data)
        kit = Item.objects.get(code='KIT')
        self.assertTrue(kit.is_assembly)
        self.assertEqual(kit.get_assembly_items().get().quantity, 4)

    def test_new_assembly_without_components(self):
        response = self.client.post(reverse('stock:NewItem'),
                                    self.data(code='kit', is_assembly='on'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Item.objects.filter(code='KIT').exists())

    def test_new_item_invalid(self):
        response = self.client.post(reverse('stock:NewItem'), self.data(code=''))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_edit_item(self):
        data = self.data(code='bolt', description='Changed')
        response = self.client.post(reverse('stock:EditItem', kwargs={'pk': self.item.pk}), data)
        self.assertRedirects(response, reverse('stock:ItemDetails', kwargs={'pk': self.item.pk}))
        self.item.refresh_from_db()
        self.assertEqual(self.item.description, 'Changed')

    def test_edit_assembly_components(self):
        nut = create_stock(code='NUT')
        kit = create_assembly(components=[(self.item, 1)])
        component = kit.get_assembly_items().get()
        data = self.data(code='kit1', **{
                'components-TOTAL_FORMS': 2, 'components-INITIAL_FORMS': 1,
                'components-0-id': component.pk, 'components-0-sub_item': self.item.pk,
                'components-0-quantity': 1, 'components-0-DELETE': 'on',
                'components-1-sub_item': nut.pk, 'components-1-quantity': 2})
        self.client.post(reverse('stock:EditItem', kwargs={'pk': kit.pk}), data)
        self.assertEqual([c.sub_item for c in kit.get_assembly_items()], [nut])

    def test_edit_missing(self):
        self.assertEqual(self.client.get(reverse('stock:EditItem', kwargs={'pk': 999})).status_code, 404)

    def test_list_filters(self):
        create_stock(code='OFF', is_active=False)
        kit = create_assembly(components=[(self.item, 1)])
        low = create_stock(code='LOW', stock_limit=3)
        url = reverse('stock:ItemsList')
        codes = lambda response: [i.code for i in response.context['object_list']]
        self.assertEqual(codes(self.client.get(url, {'search': 'hex'})), ['BOLT'])
        self.assertEqual(codes(self.client.get(url, {'status': 'disabled'})), ['OFF'])
        self.assertEqual(codes(self.client.get(url, {'status': 'assembly'})), [kit.code])
        self.assertIn('LOW', codes(self.client.get(url, {'status': 'low'})))
        self.assertNotIn('OFF', codes(self.client.get(url, {'status': 'active'})))
        self.assertEqual(len(codes(self.client.get(url, {'category': low.category.pk}))), 4)

    def test_details(self):
        add_quantity(self.item, 3)
        response = self.client.get(reverse('stock:ItemDetails', kwargs={'pk': self.item.pk}))
        self.assertContains(response, 'Hex bolt')
        self.assertEqual(len(response.context['moves_list']), 1)

    def test_delete(self):
        item = create_stock(code='TMP')
        response = self.client.post(reverse('stock:DeleteItem', kwargs={'pk': item.pk}))
        self.assertRedirects(response, reverse('stock:ItemsList'))
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())

    def test_delete_item_with_moves(self):
        add_quantity(self.item, 1)
        response = self.client.post(reverse('stock:DeleteItem', kwargs={'pk': self.item.pk}))
        self.assertTemplateUsed(response, 'error_message.html')

    def test_delete_assembly_deletes_components_links(self):
        kit = create_assembly(components=[(self.item, 1)])
        self.client.post(reverse('stock:DeleteItem', kwargs={'pk': kit.pk}))
        self.assertFalse(AssemblyItem.objects.exists())

    def test_permissions(self):
        self.client.force_login(create_user(permissions=['stock.view_item']))
        self.assertEqual(self.client.get(reverse('stock:ItemsList')).status_code, 200)
        self.assertEqual(self.client.get(reverse('stock:NewItem')).status_code, 403)
        self.assertEqual(self.client.post(
                reverse('stock:DeleteItem', kwargs={'pk': self.item.pk})).status_code, 403)
