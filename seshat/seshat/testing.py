'''
Helpers shared by the unit tests of every application
'''
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings

from customer.models import CustomerCompany, Customer
from stock import models as stock_models
from vendor.models import VendorCompany, Vendor

PASSWORD = 'Seshat-Test-Password-1'


def create_user(username='user', permissions=(), **extra_fields):
    '''
    Create a user with the given permissions ("app_label.codename")
    '''
    extra_fields.setdefault('first_name', username.capitalize())
    extra_fields.setdefault('last_name', 'Tester')
    user = get_user_model().objects.create_user(
                                    username, PASSWORD, **extra_fields)
    for name in permissions:
        app_label, codename = name.split('.')
        user.user_permissions.add(Permission.objects.get(
                                    content_type__app_label=app_label,
                                    codename=codename))
    return get_user_model().objects.get(pk=user.pk)


def create_superuser(username='admin'):
    '''
    Create an administrator
    '''
    return get_user_model().objects.create_superuser(
                    username, PASSWORD, first_name='Admin', last_name='User')


def create_stock(code='ITEM1', price='10.00', **extra_fields):
    '''
    Create an item with its category and default sub-location
    '''
    category, _ = stock_models.Category.objects.get_or_create(name='General')
    location, _ = stock_models.Location.objects.get_or_create(name='MAIN')
    sub_location, _ = stock_models.SubLocation.objects.get_or_create(
                                            location=location, name='SHELF-1')
    extra_fields.setdefault('category', category)
    extra_fields.setdefault('location', sub_location)
    return stock_models.Item.objects.create(
                                code=code, price=price, **extra_fields)


def add_quantity(item, quantity, location=None):
    '''
    Add a quantity of the item to its default (or the given) location
    '''
    return stock_models.ItemMove.objects.create(
                                item=item,
                                location=location or item.location,
                                type=stock_models.ItemMove.ADD,
                                quantity=quantity)


def create_assembly(code='KIT1', components=()):
    '''
    Create an assembled item from (item, quantity) components
    '''
    assembly = create_stock(code=code, price='50.00', is_assembly=True)
    for item, quantity in components:
        stock_models.AssemblyItem.objects.create(
                            item=assembly, sub_item=item, quantity=quantity)
    return assembly


def create_customer_company(name='Customer Co'):
    return CustomerCompany.objects.create(name=name)


def create_customer(company=None, first_name='Cus', last_name='Tomer', **extra):
    return Customer.objects.create(
                        company=company or create_customer_company(),
                        first_name=first_name, last_name=last_name, **extra)


def create_vendor_company(name='Vendor Co'):
    return VendorCompany.objects.create(name=name)


def create_vendor(company=None, first_name='Ven', last_name='Dor', **extra):
    return Vendor.objects.create(
                        company=company or create_vendor_company(),
                        first_name=first_name, last_name=last_name, **extra)


class TempDirsTestCase(TestCase):
    '''
    TestCase that keeps uploaded media and backup files in temporary folders
    '''

    @classmethod
    def setUpClass(cls):
        cls._temp_dir = tempfile.mkdtemp(prefix='seshat-tests-')
        cls._settings = override_settings(
                                MEDIA_ROOT=f'{cls._temp_dir}/media',
                                VAR_DIR=f'{cls._temp_dir}/var',
                                BACKUP_DIR=f'{cls._temp_dir}/var/backups',
                                RESTORE_DIR=f'{cls._temp_dir}/var/restores',
                                IMPORT_DIR=f'{cls._temp_dir}/var/imports',
                                EXPORT_DIR=f'{cls._temp_dir}/var/exports')
        cls._settings.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._settings.disable()
        shutil.rmtree(cls._temp_dir, ignore_errors=True)


def image_file(name='photo.png', size=(600, 600), color='teal'):
    '''
    Return an uploaded PNG image
    '''
    import io
    from PIL import Image
    from django.core.files.uploadedfile import SimpleUploadedFile
    buffer = io.BytesIO()
    Image.new('RGB', size, color).save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')
