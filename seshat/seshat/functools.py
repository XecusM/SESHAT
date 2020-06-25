from django.conf import settings
from django.apps import apps

import numpy as np
import pandas as pd
import os
import json



# Help Functions

def export_module(model_data):
    '''
    Function to export data
    '''
    if not os.path.exists(settings.EXPORT_DIR):
        if not os.path.exists(settings.VAR_DIR):
            os.makedirs(settings.VAR_DIR)

        os.makedirs(settings.EXPORT_DIR)

    model = apps.get_model(model_data['app_name'], model_data['model_name'])
    if model_data['app_name'] == 'stock' and model_data['model_name'] == 'Item':
        file_name = 'items.csv'
        if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
            os.remove(os.path.join(settings.RESTORE_DIR, file_name))
        data = pd.DataFrame.from_records(
                    model.objects.filter(
                        is_assembly=False).values_list(
                            'code', 'desciption', 'barcode', 'stock_limit',
                            'category__name', 'price',
                            'location__location__name', 'location__name',
                            'note', 'is_active',),
                            columns=(
                                'code', 'desciption', 'barcode',
                                'stock_limit', 'category', 'price',
                                'location', 'sub_location',
                                'note', 'is_active')
                    )
        data = data.set_index('code')
        data.to_csv(
                    os.path.join(settings.EXPORT_DIR, file_name),
                    encoding='utf-8')
        return {
                'message': 'items',
                'path' :os.path.join(settings.EXPORT_DIR, file_name),
                'file_name': file_name
                }
    elif model_data['app_name'] == 'stock' and model_data['model_name'] == 'Category':
        file_name = 'categories.csv'
        if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
            os.remove(os.path.join(settings.RESTORE_DIR, file_name))
        data = pd.DataFrame.from_records(
                    model.objects.all(
                        ).values_list('id', 'name'),
                            columns=('id', 'name')
                    )
        data = data.set_index('id')
        data.to_csv(
                os.path.join(settings.EXPORT_DIR, file_name),
                encoding='utf-8')
        return {
                'message': 'categories',
                'path' :os.path.join(settings.EXPORT_DIR, file_name),
                'file_name': file_name
                }
    elif model_data['app_name'] == 'stock' and model_data['model_name'] == 'SubLocation':
        file_name = 'locations.csv'
        if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
            os.remove(os.path.join(settings.RESTORE_DIR, file_name))
        data = pd.DataFrame.from_records(
                    model.objects.all(
                        ).values_list(
                            'id', 'location__name', 'name'),
                            columns=(
                                'id', 'location', 'sub_location')
                    )
        data = data.set_index('id')
        data.to_csv(
                os.path.join(settings.EXPORT_DIR, file_name),
                encoding='utf-8')
        return {
                'message': 'locations',
                'path' :os.path.join(settings.EXPORT_DIR, file_name),
                'file_name': file_name
                }
    elif model_data['app_name'] == 'customer' and model_data['model_name'] == 'Customer':
        file_name = 'customers.csv'
        if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
            os.remove(os.path.join(settings.RESTORE_DIR, file_name))
        data = pd.DataFrame.from_records(
                        model.objects.all(
                            ).values_list(
                                'id', 'company__name',
                                'first_name', 'last_name',
                                'email', 'phone', 'department',
                                'job', 'note'),
                                columns=(
                                    'id', 'company', 'barcode',
                                    'first_name', 'last_name',
                                    'email', 'phone', 'department',
                                    'job', 'note')
                        )
        data = data.set_index('id')
        data.to_csv(
                    os.path.join(settings.EXPORT_DIR, file_name),
                    encoding='utf-8')
        return {
                'message': 'customers',
                'path' :os.path.join(settings.EXPORT_DIR, file_name),
                'file_name': file_name
                }
    elif model_data['app_name'] == 'customer' and model_data['model_name'] == 'CustomerCompany':
        file_name = 'customers_companies.csv'
        if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
            os.remove(os.path.join(settings.RESTORE_DIR, file_name))
        data = pd.DataFrame.from_records(
                        model.objects.all(
                            ).values_list(
                                'name', 'desciption',
                                'phone', 'website',
                                'taxs_code', 'note'),
                                columns=(
                                    'name', 'desciption',
                                    'phone', 'website',
                                    'taxs_code', 'note')
                        )
        data = data.set_index('name')
        data.to_csv(
                    os.path.join(settings.EXPORT_DIR, file_name),
                    encoding='utf-8')
        return {
                'message': "customers' companies",
                'path' :os.path.join(settings.EXPORT_DIR, file_name),
                'file_name': file_name
                }
    elif model_data['app_name'] == 'vendor' and model_data['model_name'] == 'Vendor':
        file_name = 'vendors.csv'
        if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
            os.remove(os.path.join(settings.RESTORE_DIR, file_name))
        data = pd.DataFrame.from_records(
                        model.objects.all(
                            ).values_list(
                                'id', 'company__name',
                                'first_name', 'last_name',
                                'email', 'phone', 'department',
                                'job', 'note'),
                                columns=(
                                    'id', 'company', 'barcode',
                                    'first_name', 'last_name',
                                    'email', 'phone', 'department',
                                    'job', 'note')
                        )
        data = data.set_index('id')
        data.to_csv(
                    os.path.join(settings.EXPORT_DIR, file_name),
                    encoding='utf-8')
        return {
                'message': 'vendors',
                'path' :os.path.join(settings.EXPORT_DIR, file_name),
                'file_name': file_name
                }
    elif model_data['app_name'] == 'vendor' and model_data['model_name'] == 'VendorCompany':
        file_name = 'vendors_companies.csv'
        if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
            os.remove(os.path.join(settings.RESTORE_DIR, file_name))
        data = pd.DataFrame.from_records(
                        model.objects.all(
                            ).values_list(
                                'name', 'desciption',
                                'phone', 'website',
                                'taxs_code', 'note'),
                                columns=(
                                    'name', 'desciption',
                                    'phone', 'website',
                                    'taxs_code', 'note')
                        )
        data = data.set_index('name')
        data.to_csv(
                    os.path.join(settings.EXPORT_DIR, file_name),
                    encoding='utf-8')
        return {
                'message': "vendors' companies",
                'path' :os.path.join(settings.EXPORT_DIR, file_name),
                'file_name': file_name
                }
    else:
        return 'error'


def import_module(model_data, file_name, request_user):
    '''
    Function to import data
    '''
    if not os.path.exists(settings.IMPORT_DIR):
        if not os.path.exists(settings.VAR_DIR):
            os.makedirs(settings.VAR_DIR)

        os.makedirs(settings.IMPORT_DIR)

    model = apps.get_model(model_data['app_name'], model_data['model_name'])
    objects = list()
    data = pd.read_csv(os.path.join(settings.IMPORT_DIR, file_name))
    if model_data['app_name'] == 'stock' and model_data['model_name'] == 'Item':
        for i in list(data.index.values):
            if not model.objects.filter(code=pd_handeler(data.loc[i, 'code'])).exists():
                category_model = apps.get_model(
                                            model_data['app_name'], 'Category')
                category = category_model.objects.get_or_create(
                                            name=data.loc[i, 'category'])
                location_model = apps.get_model(
                                            model_data['app_name'], 'Location')
                location = location_model.objects.get_or_create(
                                            name=data.loc[i, 'location'])
                sub_location_model = apps.get_model(
                                            model_data['app_name'], 'SubLocation')
                sub_location = sub_location_model.objects.get_or_create(
                                                location=location[0],
                                                name=data.loc[i, 'sub_location'])

                object = model(
                                code=pd_handeler(data.loc[i, 'code']),
                                desciption=pd_handeler(data.loc[i, 'desciption']),
                                barcode=pd_handeler(data.loc[i, 'barcode']),
                                stock_limit=pd_handeler(data.loc[i, 'stock_limit']),
                                category=category[0],
                                price=pd_handeler(data.loc[i, 'price']),
                                location=sub_location[0],
                                note=pd_handeler(data.loc[i, 'note']),
                                is_active=pd_handeler(data.loc[i, 'is_active']),
                                created_by=request_user
                        )
                objects.append(object)
        message = f"({len(objects)}) items"

    elif model_data['app_name'] == 'stock' and model_data['model_name'] == 'Category':
        for i in list(data.index.values):
            if not model.objects.filter(name=pd_handeler(data.loc[i, 'name'])).exists():
                object = model(
                                name=pd_handeler(data.loc[i, 'name']),
                                created_by=request_user
                        )
                objects.append(object)
        message = f"({len(objects)}) categories"

    elif model_data['app_name'] == 'stock' and model_data['model_name'] == 'SubLocation':
        for i in list(data.index.values):
            if not model.objects.filter(name=pd_handeler(data.loc[i, 'sub_location'])).exists():
                location_model = apps.get_model(
                                            model_data['app_name'], 'Location')
                location = location_model.objects.get_or_create(
                                            name=pd_handeler(data.loc[i, 'location']))
                object = model(
                                location=location[0],
                                name=pd_handeler(data.loc[i, 'sub_location']),
                                created_by=request_user
                        )
                objects.append(object)
        message = f"({len(objects)}) locations"

    elif model_data['app_name'] == 'customer' and model_data['model_name'] == 'Customer':
        for i in list(data.index.values):
            company_model = apps.get_model(
                                    model_data['app_name'], 'CustomerCompany')
            company = company_model.objects.get_or_create(
                                        name=pd_handeler(data.loc[i, 'company']))
            object = model(
                            company=company[0],
                            first_name=pd_handeler(data.loc[i, 'first_name']),
                            last_name=pd_handeler(data.loc[i, 'last_name']),
                            email=pd_handeler(data.loc[i, 'email']),
                            department=pd_handeler(data.loc[i, 'department']),
                            job=pd_handeler(data.loc[i, 'job']),
                            note=pd_handeler(data.loc[i, 'note']),
                            created_by=request_user
                    )
            objects.append(object)
        message = f"({len(objects)}) customers"

    elif model_data['app_name'] == 'customer' and model_data['model_name'] == 'CustomerCompany':
        for i in list(data.index.values):
            if not model.objects.filter(name=pd_handeler(data.loc[i, 'name'])).exists():
                object = model(
                                name=pd_handeler(data.loc[i, 'name']),
                                desciption=pd_handeler(data.loc[i, 'desciption']),
                                phone=pd_handeler(data.loc[i, 'phone']),
                                website=pd_handeler(data.loc[i, 'website']),
                                taxs_code=pd_handeler(data.loc[i, 'taxs_code']),
                                note=pd_handeler(data.loc[i, 'note']),
                                created_by=request_user
                        )
                objects.append(object)
        message = f"({len(objects)}) customers' companies"

    elif model_data['app_name'] == 'vendor' and model_data['model_name'] == 'Vendor':
        for i in list(data.index.values):
            company_model = apps.get_model(
                                    model_data['app_name'], 'VendorCompany')
            company = company_model.objects.get_or_create(
                                        name=pd_handeler(data.loc[i, 'company']))
            object = model(
                            company=company[0],
                            first_name=pd_handeler(data.loc[i, 'first_name']),
                            last_name=pd_handeler(data.loc[i, 'last_name']),
                            email=pd_handeler(data.loc[i, 'email']),
                            department=pd_handeler(data.loc[i, 'department']),
                            job=pd_handeler(data.loc[i, 'job']),
                            note=pd_handeler(data.loc[i, 'note']),
                            created_by=request_user
                    )
            objects.append(object)
        message = f"({len(objects)}) vendors"

    elif model_data['app_name'] == 'vendor' and model_data['model_name'] == 'VendorCompany':
        for i in list(data.index.values):
            if not model.objects.filter(name=pd_handeler(data.loc[i, 'name'])).exists():
                object = model(
                                name=pd_handeler(data.loc[i, 'name']),
                                desciption=pd_handeler(data.loc[i, 'desciption']),
                                phone=pd_handeler(data.loc[i, 'phone']),
                                website=pd_handeler(data.loc[i, 'website']),
                                taxs_code=pd_handeler(data.loc[i, 'taxs_code']),
                                note=pd_handeler(data.loc[i, 'note']),
                                created_by=request_user
                        )
                objects.append(object)
        message = f"({len(objects)}) vendors' companies"

    else:
        return 'error'

    try:
        model.objects.bulk_create(objects)
        return {
                'message': message,
                'file_name': file_name
                }
    except Exception as error_type:
        print(error_type)
        return 'error'



def pd_handeler(value):
    '''
    Handele the dataframe values before save it to database
    '''
    if str(value) == str(np.nan):
        return None
    else:
        return value
