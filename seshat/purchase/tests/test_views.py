from django.test import TestCase
from django.urls import reverse

from x_django_app.models import XActivity

from purchase.models import PurchaseOrder
from purchase.tests.test_forms import lines_data
from seshat.testing import (
                        create_user, create_superuser, create_stock,
                        create_vendor_company, add_quantity, )
from stock.models import ItemMove

ORDER_MODEL = PurchaseOrder
COMPANY = create_vendor_company
APP = 'purchase'
# stock change of one ordered unit: purchases add, sales remove
SIGN = 1


class OrderViewsTest(TestCase):
    '''
    Test the order views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())
        self.company = COMPANY()
        self.item = create_stock(code='BOLT', price='2.00')
        add_quantity(self.item, 10)

    def post_data(self, rows, **extra):
        data = {'company': self.company.pk}
        data.update(extra)
        data.update(lines_data(rows))
        return data

    def create_order(self, quantity=3):
        response = self.client.post(
                    reverse(f'{APP}:NewOrder'),
                    self.post_data([{'item': self.item.pk, 'quantity': quantity, 'price': '2.00'}]))
        return response, ORDER_MODEL.objects.order_by('-id').first()

    def test_new_order_page(self):
        response = self.client.get(reverse(f'{APP}:NewOrder'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('"price": "2.00"', response.context['items_data'])

    def test_new_order(self):
        response, order = self.create_order()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual(self.item.quantity, 10 + SIGN * 3)
        self.assertEqual(order.get_activities().first().activity, XActivity.CREATE)

    def test_new_order_invalid_lines(self):
        response = self.client.post(reverse(f'{APP}:NewOrder'), self.post_data([]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ORDER_MODEL.objects.exists())

    def test_edit_order(self):
        _, order = self.create_order()
        response = self.client.get(reverse(f'{APP}:EditOrder', kwargs={'pk': order.pk}))
        self.assertEqual(response.context['formset'].initial[0]['quantity'], 3)
        data = self.post_data([{'item': self.item.pk, 'quantity': 5, 'price': '2.00'}],
                              invoice='INV-9', invoice_date='2026-03-01')
        data['lines-INITIAL_FORMS'] = 0
        response = self.client.post(reverse(f'{APP}:EditOrder', kwargs={'pk': order.pk}), data)
        self.assertRedirects(response, order.get_absolute_url())
        order.refresh_from_db()
        self.assertEqual(order.invoice, 'INV-9')
        self.assertEqual(self.item.quantity, 10 + SIGN * 5)
        self.assertEqual(ItemMove.objects.filter(item=self.item).count(), 2)

    def test_list_details(self):
        _, order = self.create_order()
        response = self.client.get(reverse(f'{APP}:OrdersList'), {'search': self.company.name})
        self.assertEqual(list(response.context['object_list']), [order])
        response = self.client.get(reverse(f'{APP}:OrdersList'), {'from_date': '2000-01-01',
                                                                  'to_date': '2000-01-02'})
        self.assertEqual(list(response.context['object_list']), [])
        self.assertContains(self.client.get(order.get_absolute_url()), 'BOLT')

    def test_delete(self):
        _, order = self.create_order()
        response = self.client.post(reverse(f'{APP}:DeleteOrder', kwargs={'pk': order.pk}))
        self.assertRedirects(response, reverse(f'{APP}:OrdersList'))
        self.assertFalse(ORDER_MODEL.objects.exists())
        self.assertEqual(self.item.quantity, 10)

    def test_permissions(self):
        _, order = self.create_order()
        self.client.force_login(create_user(permissions=[f'{APP}.view_{APP}order']))
        self.assertEqual(self.client.get(reverse(f'{APP}:OrdersList')).status_code, 200)
        self.assertEqual(self.client.get(order.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(reverse(f'{APP}:NewOrder')).status_code, 403)
        self.assertEqual(self.client.get(
                reverse(f'{APP}:EditOrder', kwargs={'pk': order.pk})).status_code, 403)
        self.assertEqual(self.client.post(
                reverse(f'{APP}:DeleteOrder', kwargs={'pk': order.pk})).status_code, 403)
        self.client.force_login(create_user('none'))
        self.assertEqual(self.client.get(reverse(f'{APP}:OrdersList')).status_code, 403)
