from decimal import Decimal

from django.test import TestCase

from sale import forms
from seshat.testing import create_stock, create_customer_company, create_assembly


def lines_data(rows, prefix='lines'):
    data = {f'{prefix}-TOTAL_FORMS': len(rows), f'{prefix}-INITIAL_FORMS': 0}
    for index, row in enumerate(rows):
        for key, value in row.items():
            data[f'{prefix}-{index}-{key}'] = value
    return data


class OrderFormTest(TestCase):
    '''
    Test the order form
    '''

    def test_valid(self):
        company = create_customer_company()
        form = forms.OrderForm(data={'company': company.pk, 'invoice': 'I-1',
                                     'invoice_date': '2026-02-01'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invoice_without_date(self):
        company = create_customer_company()
        form = forms.OrderForm(data={'company': company.pk, 'invoice': 'I-1'})
        self.assertFalse(form.is_valid())


class OrderLineFormSetTest(TestCase):
    '''
    Test the order lines formset
    '''

    def setUp(self):
        self.bolt = create_stock(code='BOLT', price='4.00')
        self.nut = create_stock(code='NUT')

    def formset(self, rows):
        return forms.OrderLineFormSet(lines_data(rows), prefix='lines')

    def test_valid_lines(self):
        formset = self.formset([
            {'item': self.bolt.pk, 'quantity': 2, 'price': '3.50'},
            {'item': self.nut.pk, 'quantity': 1, 'price': '1', 'DELETE': 'on'},
        ])
        self.assertTrue(formset.is_valid(), formset.errors)
        lines = formset.get_lines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]['price'], Decimal('3.50'))

    def test_duplicate_items(self):
        formset = self.formset([{'item': self.bolt.pk, 'quantity': 1, 'price': 1},
                                {'item': self.bolt.pk, 'quantity': 2, 'price': 1}])
        self.assertFalse(formset.is_valid())

    def test_needs_items(self):
        self.assertFalse(self.formset([]).is_valid())

    def test_quantity_must_be_positive(self):
        self.assertFalse(self.formset([{'item': self.bolt.pk, 'quantity': 0, 'price': 1}]).is_valid())

    def test_items_offered(self):
        create_assembly(components=[(self.bolt, 1)])
        create_stock(code='OFF', is_active=False)
        codes = [item.code for item in forms.ITEMS_QUERYSET()]
        self.assertEqual(codes, ITEMS_OFFERED)


# sales default the unit price to the item's price and can sell assembled items
ITEMS_OFFERED = ['BOLT', 'KIT1', 'NUT']
PRICE_REQUIRED = False


class PriceTest(TestCase):
    '''
    Test the unit price rule
    '''

    def test_price(self):
        item = create_stock(code='X', price='9.00')
        formset = forms.OrderLineFormSet(
                    lines_data([{'item': item.pk, 'quantity': 1, 'price': ''}]), prefix='lines')
        self.assertEqual(formset.is_valid(), not PRICE_REQUIRED)
        if not PRICE_REQUIRED:
            self.assertEqual(formset.get_lines()[0]['price'], Decimal('9.00'))
