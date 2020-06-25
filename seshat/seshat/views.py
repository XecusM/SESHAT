from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import (
                                LoginRequiredMixin,
                                UserPassesTestMixin,
                                PermissionRequiredMixin, )
from django.contrib.auth.decorators import (
                                        login_required,
                                        permission_required )
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

import pandas as pd
import os
import json

from . import functools
from stock import models as stock_models
from sale import models as sale_models
from purchase import models as purchase_models
from customer import models as customer_models
from report.models import Activity

# Create your views here.


class Index(LoginRequiredMixin, TemplateView):
    '''
    View for project index page
    '''
    template_name = 'seshat/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['item_list'] = sorted(
                                stock_models.Item.objects.filter(
                                    is_active=True
                                    ), key=lambda i: i.get_item_moves(
                                                            ).count())[:10]
        context['purchase_list'] = purchase_models.PurchaseOrder.objects.all(
                                                ).order_by('-created_at')[:10]
        context['sale_list'] = sale_models.SaleOrder.objects.all(
                                                ).order_by('-created_at')[:10]
        context['company_list'] = sorted(
                                customer_models.CustomerCompany.objects.all(
                                    ), key=lambda i: i.get_sale_orders(
                                                            ).count())[:10]
        return context


@login_required
@permission_required('account.backup', raise_exception=True)
def databackup(request):
    '''
    Backup all platoform database
    '''
    try:
        files = os.listdir(settings.BACKUP_DIR)
    except Exception:
        files = list()
    if request.method == 'POST':
        if 'delete' in request.POST:
            for item in request.POST:
                if settings.DUMPDATA_FILENAME in item:
                    file = files[int(item.split('-')[1])]
                    try:
                        activity = Activity.objects.create_activity(
                                            activity_object=request.user,
                                            activity=Activity.DELETE,
                                            user=request.user,
                                            message=f"Backup File {file}")

                        os.remove(os.path.join(settings.BACKUP_DIR, file))
                    except Exception as error_type:
                        activity.delete()
                        print(error_type)
                        return HttpResponse("Can't delete file(s)!")
            return render(
                        request,
                        'seshat/completed.html',
                        {
                            'message': _('Backup file(s) has been deleted'),
                            'link': reverse('backup')
                        })

        else:
            try:
                if not os.path.exists(settings.BACKUP_DIR):
                    if not os.path.exists(settings.VAR_DIR):
                        os.makedirs(settings.VAR_DIR)

                    os.makedirs(settings.BACKUP_DIR)
                file = "{0}-{1}{2}{3}{4}{5}.json".format(
                                    settings.DUMPDATA_FILENAME,
                                    timezone.now().year,
                                    timezone.now().month,
                                    timezone.now().day,
                                    timezone.now().hour,
                                    timezone.now().minute)
                activity = Activity.objects.create_activity(
                                    activity_object=request.user,
                                    activity=Activity.CREATE,
                                    user=request.user,
                                    message=f"Backup File {file}")

                dbResults = os.system(
                            'python manage.py dumpdata > {0}'.format(
                                    os.path.join(settings.BACKUP_DIR, file)))
                return render(
                            request,
                            'seshat/completed.html',
                            {
                                'message': _('Backup has completed successfully'),
                                'link': reverse('backup')
                            })
            except:
                activity.delete()
                return HttpResponse('Error in buckup process!')
    else:
        return render(request,'seshat/backup.html', {'files': files})


@login_required
@permission_required('account.backup', raise_exception=True)
def databackup_download(request, pk):
    '''
    Download the backup file
    '''
    try:
        files = os.listdir(settings.BACKUP_DIR)
        response = HttpResponse(open(os.path.join(
                                                settings.BACKUP_DIR,
                                                files[pk]
                                            ), 'rb').read())
        response['Content-Type'] = 'application/json'
        response[
            'Content-Disposition'] = "attachment; filename={0}".format(files[pk])
        Activity.objects.create_activity(
                            activity_object=request.user,
                            activity=Activity.DOWNLOAD,
                            user=request.user,
                            message=f"Backup File {files[pk]}")
        return response
    except Exception as error_type:
        print(error_type)
        return HttpResponse("File not found!")


@login_required
@permission_required('account.restore', raise_exception=True)
def datarestore(request):
    '''
    Restore all platoform database
    '''
    if request.method == 'POST' and request.FILES['restoring_file']:
        file_name = 'restore.json'
        restoring_file = request.FILES['restoring_file']
        try:
            if not os.path.exists(settings.RESTORE_DIR):
                if not os.path.exists(settings.VAR_DIR):
                    os.makedirs(settings.VAR_DIR)

                os.makedirs(settings.RESTORE_DIR)

            if os.path.isfile(os.path.join(settings.RESTORE_DIR, file_name)):
                os.remove(os.path.join(settings.RESTORE_DIR, file_name))
            backup_file = FileSystemStorage(location=settings.RESTORE_DIR)
            backup_file.save(file_name, restoring_file)
            dbResults = os.system(
                        'python manage.py loaddata {0}'.format(
                            os.path.join(settings.RESTORE_DIR, file_name)))
            Activity.objects.create_activity(
                                activity_object=request.user,
                                activity=Activity.RESTORE,
                                user=request.user,
                                message="Application database")
            return render(
                        request,
                        'seshat/completed.html',
                        {
                            'message': _('Restore has completed successfully'),
                            'link': reverse('restore')
                        })
        except Exception as error_type:
            print(error_type)
            return HttpResponse("Can't restore file!")

    else:
        return render(request,'seshat/restore.html')


@login_required
@permission_required('account.export', raise_exception=True)
def dataexport(request):
    '''
    Export data from database
    '''
    if request.method == 'POST' and 'export' in request.POST:
        model_data = {
            'app_name': request.POST['export'].split(".")[0],
            'model_name': request.POST['export'].split(".")[1]
        }
        results = functools.export_module(model_data)
        if results == 'error':
            return HttpResponse("Can't export selected module!")
        else:
            Activity.objects.create_activity(
                                activity_object=request.user,
                                activity=Activity.EXPORT,
                                user=request.user,
                                message=f"Export {results['message']}")
            response = HttpResponse(open(results['path'], 'rb').read())
            response['Content-Type'] = 'application/csv'
            response[
                'Content-Disposition'] = "attachment; filename={0}".format(
                                                        results['file_name'])
            return response
    else:
        return render(request,'seshat/export.html')


@login_required
@permission_required('account.import', raise_exception=True)
def dataimport(request):
    '''
    Import data to database
    '''
    try:
        files = [file for file in os.listdir(
                                settings.IMPORT_DIR) if '_template' in file]
    except Exception:
        files = list()

    if request.method == 'POST' and request.FILES['importing_file']:
        file_name = 'import.csv'
        if os.path.isfile(os.path.join(settings.IMPORT_DIR, file_name)):
            os.remove(os.path.join(settings.IMPORT_DIR, file_name))
        try:
            imported_file = request.FILES['importing_file']
            backup_file = FileSystemStorage(location=settings.IMPORT_DIR)
            backup_file.save(file_name, imported_file)
            model_data = {
                'app_name': request.POST['import'].split(".")[0],
                'model_name': request.POST['import'].split(".")[1]
            }
            results = functools.import_module(
                                            model_data,
                                            file_name,
                                            request.user)
        except Exception as error_type:
            print(error_type)
            results = 'error'

        if results == 'error':
            return HttpResponse("Can't import file!")
        else:
            Activity.objects.create_activity(
                                activity_object=request.user,
                                activity=Activity.IMPORT,
                                user=request.user,
                                message=f"Import {results['message']}")
            return render(
                        request,
                        'seshat/completed.html',
                            {
                                'message': "{0} {1}".format(
                                                results['message'],
                                                _('successfully imported')
                                            ),
                                'link': reverse('import')
                            })

    else:
        return render(request,'seshat/import.html', {'files': files})


@login_required
@permission_required('account.import', raise_exception=True)
def dataimport_template(request, pk):
    '''
    Download import's template file
    '''
    try:
        files = [file for file in os.listdir(
                                settings.IMPORT_DIR) if '_template' in file]
        response = HttpResponse(open(os.path.join(
                                                settings.IMPORT_DIR,
                                                files[pk]
                                            ), 'rb').read())
        response['Content-Type'] = 'application/csv'
        response[
            'Content-Disposition'] = "attachment; filename={0}".format(files[pk])
        Activity.objects.create_activity(
                            activity_object=request.user,
                            activity=Activity.DOWNLOAD,
                            user=request.user,
                            message=f"Import Template File {files[pk]}")
        return response
    except Exception as error_type:
        print(error_type)
        return HttpResponse("File not found!")


# error class views
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


def error_500(request):
    '''
    Error 500 handler
    '''
    return render(request, 'error/500.html', status=500)
