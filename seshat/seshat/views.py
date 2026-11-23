from datetime import datetime
import json
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.management import call_command
from django.db.models import Count, F, Sum, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from dateutil.relativedelta import relativedelta
from x_django_app.models import XActivity

from customer.models import CustomerCompany
from purchase.models import PurchaseOrder, PurchaseItem
from sale.models import SaleOrder, SaleItem
from stock.models import Item

from . import exports


# Help functions


def _ensure_dir(path):
    '''
    Create the folder (and its parents) when missing
    '''
    os.makedirs(path, exist_ok=True)
    return path


def _backup_files():
    '''
    List the available backup files, newest first
    '''
    if not os.path.isdir(settings.BACKUP_DIR):
        return []
    files = [
            file for file in os.listdir(settings.BACKUP_DIR)
            if file.startswith(settings.DUMPDATA_FILENAME)
            and file.endswith('.json')]
    return sorted(files, reverse=True)


def _backup_path(file_name):
    '''
    Return the full path of a backup file, or raise Http404 when the
    name is not one of the listed backup files
    '''
    if file_name not in _backup_files():
        raise Http404
    return os.path.join(settings.BACKUP_DIR, file_name)


def _monthly_totals(model, months):
    '''
    Total value (quantity x unit price) per month for order lines
    '''
    value = ExpressionWrapper(
                            F('price') * F('item__quantity'),
                            output_field=DecimalField(
                                        max_digits=16, decimal_places=2))
    rows = model.objects.filter(
                        order__created_at__date__gte=months[0]).annotate(
                        month=TruncMonth('order__created_at')).values(
                        'month').annotate(total=Sum(value))
    totals = {row['month'].strftime('%Y-%m'): float(row['total'] or 0)
              for row in rows}
    return [totals.get(month.strftime('%Y-%m'), 0) for month in months]


# Create your views here.


@login_required
def index(request):
    '''
    Project dashboard: stock health, latest orders and activity
    '''
    items = list(Item.objects.filter(is_active=True).select_related(
                                                'category', 'location'))
    low_stock = [item for item in items if item.is_low_stock]
    stock_value = sum(
                    (item.quantity * item.price for item in items
                     if not item.is_assembly), 0)

    this_month = timezone.localdate().replace(day=1)
    months = [this_month - relativedelta(months=i) for i in range(11, -1, -1)]

    context = {
        'items_count': len(items),
        'low_stock_list': low_stock[:8],
        'low_stock_count': len(low_stock),
        'stock_value': stock_value,
        'orders_count': PurchaseOrder.objects.filter(
                                created_at__year=this_month.year).count()
                        + SaleOrder.objects.filter(
                                created_at__year=this_month.year).count(),
        'purchase_list': PurchaseOrder.objects.select_related(
                                'company').order_by('-created_at')[:6],
        'sale_list': SaleOrder.objects.select_related(
                                'company').order_by('-created_at')[:6],
        'company_list': CustomerCompany.objects.annotate(
                                orders_count=Count('order_company')).filter(
                                orders_count__gt=0).order_by(
                                '-orders_count')[:6],
        'activity_list': XActivity.objects.select_related(
                                'user').order_by('-created_at')[:8],
        'chart_data': json.dumps({
            'months': [month.strftime('%Y-%m') for month in months],
            'purchases': _monthly_totals(PurchaseItem, months),
            'sales': _monthly_totals(SaleItem, months),
        }),
    }
    return render(request, 'seshat/index.html', context)


@login_required
@permission_required('account.backup', raise_exception=True)
def backup(request):
    '''
    Create, list and delete database backups
    '''
    if request.method == 'POST':
        if 'delete' in request.POST:
            deleted = 0
            for file_name in request.POST.getlist('files'):
                os.remove(_backup_path(file_name))
                XActivity.objects.create_activity(
                                activity_object=request.user,
                                activity=XActivity.DELETE,
                                user=request.user,
                                message=f"Backup File {file_name}")
                deleted += 1
            messages.success(
                        request,
                        _('%(count)s backup file(s) deleted') % {
                                                    'count': deleted})
        else:
            _ensure_dir(settings.BACKUP_DIR)
            file_name = '{0}-{1}.json'.format(
                                settings.DUMPDATA_FILENAME,
                                timezone.localtime().strftime('%Y%m%d%H%M%S'))
            call_command(
                    'dumpdata',
                    exclude=['contenttypes', 'auth.permission',
                             'sessions', 'django_db_logger'],
                    natural_foreign=True,
                    indent=2,
                    output=os.path.join(settings.BACKUP_DIR, file_name),
                    verbosity=0)
            XActivity.objects.create_activity(
                                activity_object=request.user,
                                activity=XActivity.BACKUP,
                                user=request.user,
                                message=f"Backup File {file_name}")
            messages.success(request, _('Backup has completed successfully'))
        return redirect('Backup')

    return render(request, 'seshat/backup.html', {'files': _backup_files()})


@login_required
@permission_required('account.backup', raise_exception=True)
def backup_download(request, file_name):
    '''
    Download a backup file
    '''
    path = _backup_path(file_name)
    XActivity.objects.create_activity(
                        activity_object=request.user,
                        activity=XActivity.DOWNLOAD,
                        user=request.user,
                        message=f"Backup File {file_name}")
    return FileResponse(
                    open(path, 'rb'),
                    as_attachment=True,
                    filename=file_name,
                    content_type='application/json')


@login_required
@permission_required('account.restore', raise_exception=True)
def restore(request):
    '''
    Restore the database from a backup file
    '''
    if request.method == 'POST':
        restoring_file = request.FILES.get('restoring_file')
        if not restoring_file or not restoring_file.name.endswith('.json'):
            messages.error(request, _('Please select a valid backup file'))
            return redirect('Restore')

        _ensure_dir(settings.RESTORE_DIR)
        path = os.path.join(
                    settings.RESTORE_DIR,
                    f"restore-{datetime.now():%Y%m%d%H%M%S}.json")
        with open(path, 'wb') as destination:
            for chunk in restoring_file.chunks():
                destination.write(chunk)
        try:
            call_command('loaddata', path, verbosity=0)
        except Exception as error_type:
            messages.error(
                    request,
                    _("Can't restore the selected file: %(error)s") % {
                                                    'error': error_type})
            return redirect('Restore')
        finally:
            os.remove(path)

        XActivity.objects.create_activity(
                            activity_object=request.user,
                            activity=XActivity.RESTORE,
                            user=request.user,
                            message="Application database")
        messages.success(request, _('Restore has completed successfully'))
        return redirect('Restore')

    return render(request, 'seshat/restore.html')


@login_required
@permission_required('account.export', raise_exception=True)
def export_data(request):
    '''
    Export a module's data as a CSV file
    '''
    if request.method == 'POST':
        results = exports.export_module(request.POST.get('module'))
        if results is None:
            messages.error(request, _("Can't export the selected module"))
            return redirect('Export')

        file_name, content = results
        XActivity.objects.create_activity(
                            activity_object=request.user,
                            activity=XActivity.EXPORT,
                            user=request.user,
                            message=f"Export {file_name}")
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    return render(
            request,
            'seshat/export.html',
            {'modules': exports.get_choices()})


@login_required
@permission_required('account.import', raise_exception=True)
def import_data(request):
    '''
    Import a module's data from a CSV file
    '''
    if request.method == 'POST':
        module = request.POST.get('module')
        importing_file = request.FILES.get('importing_file')
        if exports.get_module(module) is None or not importing_file:
            messages.error(
                    request,
                    _('Please select a module and a CSV file to import'))
            return redirect('Import')

        try:
            csv_text = importing_file.read().decode('utf-8')
            created = exports.import_module(module, csv_text)
        except Exception as error_type:
            messages.error(
                    request,
                    _("Can't import the selected file: %(error)s") % {
                                                    'error': error_type})
            return redirect('Import')

        XActivity.objects.create_activity(
                            activity_object=request.user,
                            activity=XActivity.IMPORT,
                            user=request.user,
                            message=f"Import {created} {module}")
        messages.success(
                    request,
                    _('%(count)s record(s) successfully imported') % {
                                                    'count': created})
        return redirect('Import')

    return render(
            request,
            'seshat/import.html',
            {'modules': exports.get_choices()})


@login_required
@permission_required('account.import', raise_exception=True)
def import_template(request, module):
    '''
    Download the CSV template of a module
    '''
    results = exports.export_template(module)
    if results is None:
        raise Http404
    file_name, content = results
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


# Error handlers


def error_400(request, exception):
    '''
    Error 400 handler
    '''
    return render(request, 'error/400.html', status=400)


def error_403(request, exception):
    '''
    Error 403 handler
    '''
    return render(request, 'error/403.html', status=403)


def error_404(request, exception):
    '''
    Error 404 handler
    '''
    return render(request, 'error/404.html', status=404)


def error_405(request, exception=None):
    '''
    Error 405 handler
    '''
    return render(request, 'error/405.html', status=405)


def error_500(request):
    '''
    Error 500 handler
    '''
    return render(request, 'error/500.html', status=500)
