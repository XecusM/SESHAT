from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from . import models

######################################################################
# Permissions shown on the user's permissions page, grouped by application
permissions = [
    {
        'title': 'account',
        'label': _('Administration'),
        'permissions': [
                ('account.view_user', _('View user')),
                ('account.add_user', _('Add user')),
                ('account.change_user', _('Edit user')),
                ('account.delete_user', _('Delete user')),
                ('account.view_activity', _('View activity')),
                ('account.reset_password', _('Reset password')),
                ('account.report_activity', _('View Activity Report')),
                ('account.import', _('Import data')),
                ('account.export', _('Export data')),
                ('account.backup', _('Backup database')),
                ('account.restore', _('Restore database')), ]},
    {
        'title': 'django_db_logger',
        'label': _('Log Entries'),
        'permissions': [
                ('django_db_logger.view_statuslog', _('View log entries')), ]},
    {
        'title': 'stock',
        'label': _('Stock'),
        'permissions': [
                ('stock.view_item', _('View Stock')),
                ('stock.add_item', _('Add Item')),
                ('stock.change_item', _('Edit Item')),
                ('stock.delete_item', _('Delete Item')),
                ('stock.add_category', _('Add Category')),
                ('stock.change_category', _('Edit Category')),
                ('stock.delete_category', _('Delete Category')),
                ('stock.add_location', _('Add Location')),
                ('stock.change_location', _('Edit Location')),
                ('stock.delete_location', _('Delete Location')),
                ('stock.add_sublocation', _('Add Sub-location')),
                ('stock.change_sublocation', _('Edit Sub-location')),
                ('stock.delete_sublocation', _('Delete Sub-location')),
                ('stock.add_itemmove', _('Move Item')),
                ('stock.add_itemtransfer', _('Transfer Item')), ]},
    {
        'title': 'customer',
        'label': _('Customers'),
        'permissions': [
                ('customer.view_customercompany', _('View Company')),
                ('customer.add_customercompany', _('Add Company')),
                ('customer.change_customercompany', _('Edit Company')),
                ('customer.delete_customercompany', _('Delete Company')),
                ('customer.view_customer', _('View Customer')),
                ('customer.add_customer', _('Add Customer')),
                ('customer.change_customer', _('Edit Customer')),
                ('customer.delete_customer', _('Delete Customer')), ]},
    {
        'title': 'vendor',
        'label': _('Vendors'),
        'permissions': [
                ('vendor.view_vendorcompany', _('View Company')),
                ('vendor.add_vendorcompany', _('Add Company')),
                ('vendor.change_vendorcompany', _('Edit Company')),
                ('vendor.delete_vendorcompany', _('Delete Company')),
                ('vendor.view_vendor', _('View Vendor')),
                ('vendor.add_vendor', _('Add Vendor')),
                ('vendor.change_vendor', _('Edit Vendor')),
                ('vendor.delete_vendor', _('Delete Vendor')), ]},
    {
        'title': 'purchase',
        'label': _('Purchases'),
        'permissions': [
                ('purchase.view_purchaseorder', _('View Order')),
                ('purchase.add_purchaseorder', _('Add Order')),
                ('purchase.change_purchaseorder', _('Edit Order')),
                ('purchase.delete_purchaseorder', _('Delete Order')), ]},
    {
        'title': 'sale',
        'label': _('Sales'),
        'permissions': [
                ('sale.view_saleorder', _('View Order')),
                ('sale.add_saleorder', _('Add Order')),
                ('sale.change_saleorder', _('Edit Order')),
                ('sale.delete_saleorder', _('Delete Order')), ]},
]

# Any permission on the left implies the "view" permission on the right
implied_permissions = [
    ([
        'account.add_user', 'account.change_user', 'account.delete_user',
        'account.view_activity', 'account.reset_password',
        'account.report_activity'], 'account.view_user'),
    ([
        'stock.add_item', 'stock.change_item', 'stock.delete_item',
        'stock.add_category', 'stock.change_category', 'stock.delete_category',
        'stock.add_location', 'stock.change_location', 'stock.delete_location',
        'stock.add_sublocation', 'stock.change_sublocation',
        'stock.delete_sublocation', 'stock.add_itemmove',
        'stock.add_itemtransfer', 'purchase.view_purchaseorder',
        'sale.view_saleorder'], 'stock.view_item'),
    ([
        'customer.add_customercompany', 'customer.change_customercompany',
        'customer.delete_customercompany', 'customer.view_customer',
        'customer.add_customer', 'customer.change_customer',
        'customer.delete_customer', 'sale.view_saleorder'],
        'customer.view_customercompany'),
    ([
        'customer.add_customer', 'customer.change_customer',
        'customer.delete_customer'], 'customer.view_customer'),
    ([
        'vendor.add_vendorcompany', 'vendor.change_vendorcompany',
        'vendor.delete_vendorcompany', 'vendor.view_vendor',
        'vendor.add_vendor', 'vendor.change_vendor',
        'vendor.delete_vendor', 'purchase.view_purchaseorder'],
        'vendor.view_vendorcompany'),
    ([
        'vendor.add_vendor', 'vendor.change_vendor',
        'vendor.delete_vendor'], 'vendor.view_vendor'),
    ([
        'purchase.add_purchaseorder', 'purchase.change_purchaseorder',
        'purchase.delete_purchaseorder'], 'purchase.view_purchaseorder'),
    ([
        'sale.add_saleorder', 'sale.change_saleorder',
        'sale.delete_saleorder'], 'sale.view_saleorder'),
]
######################################################################


def all_permission_names():
    '''
    Return every permission name ("app_label.codename") on the page
    '''
    return [item[0] for group in permissions for item in group['permissions']]


def get_permission(name):
    '''
    Return the Permission object for "app_label.codename", or None
    '''
    app_label, codename = name.split('.', 1)
    return Permission.objects.filter(
                            content_type__app_label=app_label,
                            codename=codename).first()


def get_user_permission_names(user):
    '''
    Return the names of the permissions given directly to the user
    '''
    return {
        f'{app_label}.{codename}' for app_label, codename in
        user.user_permissions.values_list(
                                'content_type__app_label', 'codename')}


def set_permissions(user, selected):
    '''
    Give the user exactly the selected permissions (from the permissions
    page list), then add the implied "view" permissions
    '''
    selected = set(selected)
    for name in all_permission_names():
        permission = get_permission(name)
        if permission is None:
            continue
        if name in selected:
            user.user_permissions.add(permission)
        else:
            user.user_permissions.remove(permission)

    check_permissions(user)


def check_permissions(user):
    '''
    Add the "view" permission implied by add, change and delete permissions.
    Repeated until nothing changes, so chains of implications are applied.
    '''
    changed = True
    while changed:
        changed = False
        names = get_user_permission_names(user)
        for sources, target in implied_permissions:
            if target not in names and names.intersection(sources):
                permission = get_permission(target)
                if permission is not None:
                    user.user_permissions.add(permission)
                    changed = True


def get_url_link(user):
    '''
    Return the url of the user's default page
    '''
    pages = {
        models.Settings.INDEX: 'Index',
        models.Settings.ADMIN: 'account:Index',
        models.Settings.STOCK: 'stock:Index',
        models.Settings.CUSTOMER: 'customer:CompaniesList',
        models.Settings.VENDOR: 'vendor:CompaniesList',
        models.Settings.PURCHASE: 'purchase:OrdersList',
        models.Settings.SALE: 'sale:OrdersList',
    }
    return reverse(pages.get(user.user_settings.default_page, 'Index'))
