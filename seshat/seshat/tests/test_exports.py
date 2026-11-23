from django.core.exceptions import ValidationError
from django.test import TestCase

from customer.models import Customer, CustomerCompany
from seshat import exports
from seshat.testing import create_stock, create_vendor
from stock.models import Item, Category, SubLocation
from vendor.models import Vendor


class ExportsTest(TestCase):
    '''
    Test the CSV export engine
    '''

    def test_choices_cover_all_modules(self):
        self.assertEqual([key for key, _ in exports.get_choices()], list(exports.MODULES))
        self.assertIsNone(exports.get_module('nope'))

    def test_export_items_excludes_assemblies(self):
        create_stock(code='A1', description='Anchor')
        create_stock(code='KIT', is_assembly=True)
        file_name, content = exports.export_module('stock.Item')
        lines = content.splitlines()
        self.assertEqual(file_name, 'items.csv')
        self.assertTrue(lines[0].startswith('code,description'))
        self.assertEqual(len(lines), 2)
        self.assertIn('Anchor', lines[1])

    def test_export_vendor(self):
        create_vendor(first_name='Vic')
        _, content = exports.export_module('vendor.Vendor')
        self.assertIn('Vendor Co,Vic,Dor', content)

    def test_export_unknown(self):
        self.assertIsNone(exports.export_module('auth.User'))
        self.assertIsNone(exports.export_template('auth.User'))

    def test_export_template(self):
        file_name, content = exports.export_template('stock.Category')
        self.assertEqual(file_name, 'categories_template.csv')
        self.assertEqual(content.strip(), 'name')


class ImportsTest(TestCase):
    '''
    Test the CSV import engine
    '''

    def test_import_items_creates_related_records(self):
        csv_text = ('﻿code,description,barcode,stock_limit,category,price,'
                    'location,sub_location,note,is_active\n'
                    'b1,Bolt,,5,bolts,2.5,main,a1,,true\n'
                    'b1,Duplicate,,,bolts,1,main,a1,,true\n')
        self.assertEqual(exports.import_module('stock.Item', csv_text), 1)
        item = Item.objects.get(code='B1')
        self.assertEqual(item.category.name, 'Bolts')
        self.assertEqual(str(item.location), 'MAIN / A1')
        self.assertEqual(item.stock_limit, 5)

    def test_import_categories_and_locations(self):
        self.assertEqual(exports.import_module('stock.Category', 'name\ntools\n\n'), 1)
        self.assertTrue(Category.objects.filter(name='Tools').exists())
        self.assertEqual(exports.import_module(
                    'stock.SubLocation', 'location,sub_location\nstore,b2\n'), 1)
        self.assertTrue(SubLocation.objects.filter(name='B2', location__name='STORE').exists())

    def test_import_companies_and_contacts(self):
        header = 'name,description,phone,website,tax_code,note\n'
        self.assertEqual(exports.import_module(
                    'customer.CustomerCompany', header + 'Acme,,,,,\nAcme,,,,,\n'), 1)
        contacts = 'company,first_name,last_name,email,phone,department,job,note\n'
        self.assertEqual(exports.import_module(
                    'customer.Customer', contacts + 'Acme,Ann,Lee,ann@a.com,,,,\n,No,Company,,,,,\n'), 1)
        self.assertEqual(Customer.objects.get().company, CustomerCompany.objects.get(name='Acme'))
        self.assertEqual(exports.import_module(
                    'vendor.Vendor', contacts + 'Parts Ltd,Vic,Tor,,,,,\n'), 1)
        self.assertEqual(Vendor.objects.get().company.name, 'Parts Ltd')

    def test_import_missing_columns(self):
        with self.assertRaises(ValueError):
            exports.import_module('stock.Category', 'wrong\nx\n')

    def test_import_unknown_module(self):
        with self.assertRaises(ValueError):
            exports.import_module('auth.User', 'name\n')

    def test_import_invalid_row_rolls_back(self):
        csv_text = ('name,description,phone,website,tax_code,note\n'
                    'Good,,,,,\nBad,,not-a-phone,,,\n')
        with self.assertRaises(ValidationError):
            exports.import_module('vendor.VendorCompany', csv_text)
        self.assertEqual(Vendor.objects.count(), 0)
        from vendor.models import VendorCompany
        self.assertEqual(VendorCompany.objects.count(), 0)
