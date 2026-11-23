'''
The shared CSV import/export engine.

Every module that can be exported or imported is described once in
MODULES: the CSV columns, the model fields they map to, and how a row is
turned back into a database record.
'''
import csv
import io

from django.apps import apps
from django.db import transaction
from django.utils.translation import gettext_lazy as _


def _value(row, column):
    '''
    Get a cleaned CSV value: empty strings become None
    '''
    value = row.get(column)
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _boolean(value, default=True):
    '''
    Convert a CSV value to a boolean
    '''
    if value is None:
        return default
    return str(value).strip().lower() in ('true', '1', 'yes', 'y')


def _get_or_create(model_label, **kwargs):
    '''
    Get or create a related record by its natural fields
    '''
    model = apps.get_model(model_label)
    return model.objects.get_or_create(**kwargs)[0]


# Row builders: return an unsaved instance, or None to skip the row


def _build_item(model, row):
    code = _value(row, 'code')
    if not code or model.objects.filter(code=code.upper()).exists():
        return None
    location = _get_or_create(
                        'stock.Location',
                        name=(_value(row, 'location') or 'MAIN').upper())
    sub_location = _get_or_create(
                        'stock.SubLocation',
                        location=location,
                        name=(_value(row, 'sub_location') or 'MAIN').upper())
    category = _get_or_create(
                        'stock.Category',
                        name=(_value(row, 'category') or 'General').capitalize())
    return model(
                code=code.upper(),
                description=_value(row, 'description'),
                barcode=_value(row, 'barcode'),
                stock_limit=_value(row, 'stock_limit'),
                category=category,
                price=_value(row, 'price') or 0,
                location=sub_location,
                note=_value(row, 'note'),
                is_active=_boolean(_value(row, 'is_active')))


def _build_category(model, row):
    name = _value(row, 'name')
    if not name or model.objects.filter(name=name.capitalize()).exists():
        return None
    return model(name=name.capitalize())


def _build_sub_location(model, row):
    name = _value(row, 'sub_location')
    if not name or model.objects.filter(name=name.upper()).exists():
        return None
    location = _get_or_create(
                        'stock.Location',
                        name=(_value(row, 'location') or 'MAIN').upper())
    return model(location=location, name=name.upper())


def _build_company(model, row):
    name = _value(row, 'name')
    if not name or model.objects.filter(name=name).exists():
        return None
    return model(
                name=name,
                description=_value(row, 'description'),
                phone=_value(row, 'phone'),
                website=_value(row, 'website'),
                tax_code=_value(row, 'tax_code'),
                note=_value(row, 'note'))


def _contact_builder(company_label):
    def build(model, row):
        first_name = _value(row, 'first_name')
        last_name = _value(row, 'last_name')
        company_name = _value(row, 'company')
        if not (first_name and last_name and company_name):
            return None
        email = _value(row, 'email')
        if email and model.objects.filter(email=email).exists():
            return None
        company = _get_or_create(company_label, name=company_name)
        return model(
                    company=company,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=_value(row, 'phone'),
                    department=_value(row, 'department'),
                    job=_value(row, 'job'),
                    note=_value(row, 'note'))
    return build


MODULES = {
    'stock.Item': {
        'label': _('Items'),
        'file_name': 'items',
        'columns': [
                    'code', 'description', 'barcode', 'stock_limit',
                    'category', 'price', 'location', 'sub_location',
                    'note', 'is_active'],
        'fields': [
                    'code', 'description', 'barcode', 'stock_limit',
                    'category__name', 'price', 'location__location__name',
                    'location__name', 'note', 'is_active'],
        'filter': {'is_assembly': False},
        'build': _build_item,
    },
    'stock.Category': {
        'label': _('Categories'),
        'file_name': 'categories',
        'columns': ['name'],
        'fields': ['name'],
        'build': _build_category,
    },
    'stock.SubLocation': {
        'label': _('Locations'),
        'file_name': 'locations',
        'columns': ['location', 'sub_location'],
        'fields': ['location__name', 'name'],
        'build': _build_sub_location,
    },
    'customer.CustomerCompany': {
        'label': _("Customers' companies"),
        'file_name': 'customer_companies',
        'columns': [
                    'name', 'description', 'phone',
                    'website', 'tax_code', 'note'],
        'fields': [
                    'name', 'description', 'phone',
                    'website', 'tax_code', 'note'],
        'build': _build_company,
    },
    'customer.Customer': {
        'label': _('Customers'),
        'file_name': 'customers',
        'columns': [
                    'company', 'first_name', 'last_name', 'email',
                    'phone', 'department', 'job', 'note'],
        'fields': [
                    'company__name', 'first_name', 'last_name', 'email',
                    'phone', 'department', 'job', 'note'],
        'build': _contact_builder('customer.CustomerCompany'),
    },
    'vendor.VendorCompany': {
        'label': _("Vendors' companies"),
        'file_name': 'vendor_companies',
        'columns': [
                    'name', 'description', 'phone',
                    'website', 'tax_code', 'note'],
        'fields': [
                    'name', 'description', 'phone',
                    'website', 'tax_code', 'note'],
        'build': _build_company,
    },
    'vendor.Vendor': {
        'label': _('Vendors'),
        'file_name': 'vendors',
        'columns': [
                    'company', 'first_name', 'last_name', 'email',
                    'phone', 'department', 'job', 'note'],
        'fields': [
                    'company__name', 'first_name', 'last_name', 'email',
                    'phone', 'department', 'job', 'note'],
        'build': _contact_builder('vendor.VendorCompany'),
    },
}


def get_choices():
    '''
    Modules list for the export / import select boxes
    '''
    return [(key, module['label']) for key, module in MODULES.items()]


def get_module(key):
    '''
    Return the module definition, or None for an unknown key
    '''
    return MODULES.get(key)


def export_module(key):
    '''
    Export the module's records as CSV text.
    Returns (file_name, csv_text), or None for an unknown module.
    '''
    module = get_module(key)
    if module is None:
        return None

    model = apps.get_model(key)
    queryset = model.objects.filter(**module.get('filter', {}))
    queryset = queryset.order_by('pk').values_list(*module['fields'])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(module['columns'])
    for row in queryset:
        writer.writerow(['' if value is None else value for value in row])

    return f"{module['file_name']}.csv", output.getvalue()


def export_template(key):
    '''
    Return (file_name, csv_text) with the module's header row only,
    used as the import template. None for an unknown module.
    '''
    module = get_module(key)
    if module is None:
        return None

    output = io.StringIO()
    csv.writer(output).writerow(module['columns'])
    return f"{module['file_name']}_template.csv", output.getvalue()


def import_module(key, csv_text):
    '''
    Import CSV text into the module. Rows whose unique values already
    exist are skipped. Returns the number of created records.
    Raises ValueError for an unknown module or a file without the
    expected columns.
    '''
    module = get_module(key)
    if module is None:
        raise ValueError(f'Unknown module: {key}')

    reader = csv.DictReader(io.StringIO(csv_text.lstrip('﻿')))
    missing = set(module['columns']) - set(reader.fieldnames or [])
    if missing:
        raise ValueError(
                'Missing columns: ' + ', '.join(sorted(missing)))

    model = apps.get_model(key)
    created = 0
    with transaction.atomic():
        for row in reader:
            instance = module['build'](model, row)
            if instance is None:
                continue
            instance.full_clean()
            instance.save()
            created += 1

    return created
