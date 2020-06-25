from django.shortcuts import render
from django.views.generic import (
                                TemplateView, CreateView,
                                UpdateView, ListView, DetailView)
from django.contrib.auth.mixins import (
                                LoginRequiredMixin,
                                UserPassesTestMixin,
                                PermissionRequiredMixin, )
from django.contrib.auth.decorators import (
                                            login_required,
                                            permission_required )
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from x_django_app.views import XListView

from report.models import Activity
from report.views import RCreateView, RUpdateView, record_delete_object
from vendor import forms, models as vendors_models

# Create your views here.


class CreateCompany(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RCreateView):
    '''
    Create a new company view
    '''
    permission_required = ('vendor.add_vendorcompany',)
    template_name = 'vendor/company_new.html'
    model = vendors_models.VendorCompany
    form_class = forms.CompanyForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Company-{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        if self.request.GET.get('next'):
            reverse(self.request.GET.get('next'))
        else:
            return reverse_lazy(
                                'vendor:company_details',
                                kwargs={'pk': self.object.pk})


class EditCompany(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RUpdateView):
    '''
    Edit an existing company view
    '''
    permission_required = ('vendor.change_vendorcompany',)
    template_name = 'vendor/company_edit.html'
    model = vendors_models.VendorCompany
    form_class = forms.CompanyForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Company-{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        if self.request.GET.get('next'):
            reverse(self.request.GET.get('next'))
        else:
            return reverse_lazy(
                                'vendor:company_details',
                                kwargs={'pk': self.object.pk})


class CompaniesList(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    List of all companies
    '''
    permission_required = ('vendor.view_vendorcompany',)
    template_name = 'vendor/companies_list.html'
    model = vendors_models.VendorCompany
    search_fields = ['name', 'desciption', 'phone']
    queryset = vendors_models.VendorCompany.objects.all()
    ordering = ('name', )

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class CompanyDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View company details
    '''
    permission_required = ('vendor.view_vendorcompany',)
    template_name = 'vendor/company_details.html'
    model = vendors_models.VendorCompany
    queryset = vendors_models.VendorCompany.objects.all()


class CreateVendor(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RCreateView):
    '''
    Create a new vendor view
    '''
    permission_required = ('vendor.add_vendor',)
    template_name = 'vendor/vendor_new.html'
    model = vendors_models.Vendor
    form_class = forms.VendorForm

    def get_context_data(self, **kwargs):
        '''
        add extra context to template
        '''
        context = super().get_context_data(**kwargs)
        context['company'] = vendors_models.VendorCompany.objects.get(
                                                    id=self.kwargs['pk'])
        return context

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return "Vendor-{0}-{1}".format(
                                        self.object.company.name,
                                        self.object.full_name)

    def get_success_url(self):
        '''
        Method after success post
        '''
        if self.request.GET.get('next'):
            reverse(self.request.GET.get('next'))
        else:
            return reverse_lazy(
                                'vendor:vendor_details',
                                kwargs={'pk': self.object.pk})


class EditVendor(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RUpdateView):
    '''
    Edit an existing vendor view
    '''
    permission_required = ('vendor.change_vendor',)
    template_name = 'vendor/vendor_edit.html'
    model = vendors_models.Vendor
    form_class = forms.VendorForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return "Vendor-{0}-{1}".format(
                                        self.object.company.name,
                                        self.object.full_name)

    def get_context_data(self, **kwargs):
        '''
        add extra context to template
        '''
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('next'):
            kwargs.update({'next': self.request.GET.get('next')})
            context.update(kwargs)
        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        if self.request.GET.get('next'):
            reverse(self.request.GET.get('next'))
        else:
            return reverse_lazy(
                                'vendor:vendor_details',
                                kwargs={'pk': self.object.pk})


class VendorsList(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    List of all vendors
    '''
    permission_required = ('vendor.view_vendor',)
    template_name = 'vendor/vendors_list.html'
    model = vendors_models.Vendor
    search_fields = ['first_name', 'last_name', ]
    queryset = vendors_models.Vendor.objects.all()
    ordering = ('first_name', 'last_name')

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class VendorDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View vendor details
    '''
    permission_required = ('vendor.view_vendor',)
    template_name = 'vendor/vendor_details.html'
    model = vendors_models.Vendor
    queryset = vendors_models.Vendor.objects.all()


# Function Views


@login_required
@permission_required('vendor.delete_vendorcompany', raise_exception=True)
def company_delete(request, pk):
    '''
    Delete company
    '''
    if request.method == "POST":
        company = get_object_or_404(vendors_models.VendorCompany, pk=pk)
        # store user activity
        delete_object = record_delete_object(
                                        request,
                                        company,
                                        f"Company-{company.name}")

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('vendor:companies_list')
        else:
            return render(request, 'vendor/error_message.html', {
                    'message': _("Couldn't delete the selected company"),
                    'link': reverse('vendor:companies_list')})
    else:
        raise Http404


@login_required
@permission_required('vendor.delete_vendor', raise_exception=True)
def vendor_delete(request, pk):
    '''
    Delete vendor
    '''
    if request.method == "POST":
        vendor = get_object_or_404(vendors_models.Vendor, pk=pk)
        # store user activity
        delete_object =  record_delete_object(
                                        request,
                                        vendor,
                                        "Vendor-{0}-{1}".format(
                                                    vendor.company.name,
                                                    vendor.full_name))

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('vendor:vendors_list')
        else:
            return render(request, 'vendor/error_message.html', {
                    'message': _("Couldn't delete the selected vendor"),
                    'link': reverse('vendor:vendors_list')})
    else:
        raise Http404
