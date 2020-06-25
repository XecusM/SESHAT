from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from . import models

######################################################################
# Permisssions
permissions = [{
                'title': 'Accounts',
                'permissions': [
                        ('add_user', _('Add user')),
                        ('change_user', _('Edit user')),
                        ('delete_user', _('Delete user')),
                        ('view_user', _('View user')),
                        ('view_activity', _('View activity')),
                        ('reset_password', _('Reset password')),
                        ("import", _("Import data")),
                        ("export", _("Export data")),
                        ("backup", _("Backup database")),
                        ("restore", _("Restore database")), ]},
                {
                'title': 'stock',
                'permissions': [
                        ('add_category', _('Add Category')),
                        ('change_category', _('Edit Category')),
                        ('delete_category', _('Delete Category')),
                        ('add_item', _('Add Item')),
                        ('change_item', _('Edit Item')),
                        ('delete_item', _('Delete Item')),
                        ('add_location', _('Add Location')),
                        ('change_location', _('Edit Location')),
                        ('delete_location', _('Delete Location')),
                        ('add_sublocation', _('Add Sub-location')),
                        ('change_sublocation', _('Edit Sub-location')),
                        ('delete_sublocation', _('Delete Sub-location')),
                        ('add_itemmove', _('Move Item')),
                        ('add_itemtransfer', _('Tranfer move')), ]},
                {
                'title': 'Customer',
                'permissions': [
                        ('add_customercompany', _('Add Company')),
                        ('change_customercompany', _('Edit Company')),
                        ('delete_customercompany', _('Delete Company')),
                        ('view_customercompany', _('View Company')),
                        ('add_customer', _('Add Customer')),
                        ('change_customer', _('Edit Customer')),
                        ('delete_customer', _('Delete Customer')),
                        ('view_customer', _('View Customer')), ]},
                {
                'title': 'Vendor',
                'permissions': [
                        ('add_vendorcompany', _('Add Company')),
                        ('change_vendorcompany', _('Edit Company')),
                        ('delete_vendorcompany', _('Delete Company')),
                        ('view_vendorcompany', _('View Company')),
                        ('add_vendor', _('Add Vendor')),
                        ('change_vendor', _('Edit Vendor')),
                        ('delete_vendor', _('Delete Vendor')),
                        ('view_vendor', _('View Vendor')), ]},
                {
                'title': 'Purchase',
                'permissions': [
                        ('add_purchaseorder', _('Add Order')),
                        ('change_purchaseorder', _('Edit Order')),
                        ('delete_purchaseorder', _('Delete Order')), ]},
                {
                'title': 'Sale',
                'permissions': [
                        ('add_saleorder', _('Add Order')),
                        ('change_saleorder', _('Edit Order')),
                        ('delete_saleorder', _('Delete Order')), ]},
]
######################################################################


def check_permisssions(user):
    '''
    Add view permission for add, change and delete permissions
    '''
    users_permissions = [
                        'add_user',
                        'change_user',
                        'delete_user',
                        'view_activity',
                        'reset_password']

    for permission in users_permissions:
        user_permission = Permission.objects.get(
                                            codename=permission)
        if user.user_permissions.filter(
                            id=user_permission.id).exists():
            view_permission = Permission.objects.get(
                                        codename='view_user')
            user.user_permissions.add(view_permission)

    users_permissions = [
                        'add_customercompany',
                        'change_customercompany',
                        'delete_customercompany',
                        'add_customer',
                        'change_customer',
                        'delete_customer',
                        'view_customer']

    for permission in users_permissions:
        user_permission = Permission.objects.get(
                                            codename=permission)
        if user.user_permissions.filter(
                            id=user_permission.id).exists():
            view_permission = Permission.objects.get(
                                        codename='view_customercompany')
            user.user_permissions.add(view_permission)

    users_permissions = [
                        'add_vendorcompany',
                        'change_vendorcompany',
                        'delete_vendorcompany',
                        'add_vendor',
                        'change_vendor',
                        'delete_vendor',
                        'view_vendor']

    for permission in users_permissions:
        user_permission = Permission.objects.get(
                                            codename=permission)
        if user.user_permissions.filter(
                            id=user_permission.id).exists():
            view_permission = Permission.objects.get(
                                        codename='view_vendorcompany')
            user.user_permissions.add(view_permission)

    users_permissions = [
                        'add_customer',
                        'change_customer',
                        'delete_customer']

    for permission in users_permissions:
        user_permission = Permission.objects.get(
                                            codename=permission)
        if user.user_permissions.filter(
                            id=user_permission.id).exists():
            view_permission = Permission.objects.get(
                                        codename='view_customer')
            user.user_permissions.add(view_permission)

    users_permissions = [
                        'add_vendor',
                        'change_vendor',
                        'delete_vendor']

    for permission in users_permissions:
        user_permission = Permission.objects.get(
                                            codename=permission)
        if user.user_permissions.filter(
                            id=user_permission.id).exists():
            view_permission = Permission.objects.get(
                                        codename='view_vendor')
            user.user_permissions.add(view_permission)


def get_url_link(user, url):
    '''
    return the url link from its name
    '''
    if user.user_settings.default_page == models.UserSettings.INDEX:
        return reverse('index')
    if user.user_settings.default_page == models.UserSettings.ADMIN:
        return reverse('account:index')
    if user.user_settings.default_page == models.UserSettings.STOCK:
        return reverse('stock:index')
    if user.user_settings.default_page == models.UserSettings.CUSTOMER:
        return reverse('customer:customers_list')
    if user.user_settings.default_page == models.UserSettings.VENDOR:
        return reverse('vendor:vendors_list')
    if user.user_settings.default_page == models.UserSettings.PURCHASE:
        return reverse('purchase:orders_list')
    if user.user_settings.default_page == models.UserSettings.SALE:
        return reverse('sale:orders_list')
