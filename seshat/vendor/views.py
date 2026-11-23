from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from x_django_app.views import XCreateView, XUpdateView, XListView

from seshat.functools import PaginateMixin, NextUrlMixin, delete_object

from . import forms, models

# Create your views here.


class NewCompany(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                NextUrlMixin,
                XCreateView):
    '''
    Create a new company view
    '''
    permission_required = ('vendor.add_vendorcompany',)
    template_name = 'vendor/company_new.html'
    model = models.VendorCompany
    form_class = forms.CompanyForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Company-{object.name}"


class EditCompany(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                NextUrlMixin,
                XUpdateView):
    '''
    Edit an existing company view
    '''
    permission_required = ('vendor.change_vendorcompany',)
    template_name = 'vendor/company_edit.html'
    model = models.VendorCompany
    form_class = forms.CompanyForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Company-{object.name}"


class CompaniesList(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    PaginateMixin,
                    XListView):
    '''
    List of all companies
    '''
    permission_required = ('vendor.view_vendorcompany',)
    template_name = 'vendor/companies_list.html'
    model = models.VendorCompany
    search_fields = ['name', 'description', 'phone', 'tax_code']
    queryset = models.VendorCompany.objects.all()
    ordering = ('name', )


class CompanyDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View company details
    '''
    permission_required = ('vendor.view_vendorcompany',)
    template_name = 'vendor/company_details.html'
    model = models.VendorCompany


class NewVendor(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                NextUrlMixin,
                XCreateView):
    '''
    Create a new vendor view
    '''
    permission_required = ('vendor.add_vendor',)
    template_name = 'vendor/vendor_new.html'
    model = models.Vendor
    form_class = forms.VendorForm

    def get_initial(self):
        '''
        Pre-select the company sent in the url
        '''
        initial = super().get_initial()
        if self.request.GET.get('company'):
            initial['company'] = self.request.GET.get('company')
        return initial

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Vendor-{object.company.name}-{object.full_name}"


class EditVendor(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                NextUrlMixin,
                XUpdateView):
    '''
    Edit an existing vendor view
    '''
    permission_required = ('vendor.change_vendor',)
    template_name = 'vendor/vendor_edit.html'
    model = models.Vendor
    form_class = forms.VendorForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Vendor-{object.company.name}-{object.full_name}"


class VendorsList(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    PaginateMixin,
                    XListView):
    '''
    List of all vendors
    '''
    permission_required = ('vendor.view_vendor',)
    template_name = 'vendor/vendors_list.html'
    model = models.Vendor
    search_fields = [
                    'first_name', 'last_name', 'email',
                    'phone', 'company__name']
    queryset = models.Vendor.objects.select_related('company')
    ordering = ('first_name', 'last_name')


class VendorDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View vendor details
    '''
    permission_required = ('vendor.view_vendor',)
    template_name = 'vendor/vendor_details.html'
    model = models.Vendor


# Function Views


@login_required
@permission_required('vendor.delete_vendorcompany', raise_exception=True)
@require_POST
def delete_company(request, pk):
    '''
    Delete company
    '''
    return delete_object(
                    request,
                    models.VendorCompany,
                    pk,
                    lambda company: f"Company-{company.name}",
                    reverse('vendor:CompaniesList'),
                    reverse('vendor:CompanyDetails', kwargs={'pk': pk}))


@login_required
@permission_required('vendor.delete_vendor', raise_exception=True)
@require_POST
def delete_vendor(request, pk):
    '''
    Delete vendor
    '''
    return delete_object(
                    request,
                    models.Vendor,
                    pk,
                    lambda vendor: "Vendor-{0}-{1}".format(
                                                vendor.company.name,
                                                vendor.full_name),
                    reverse('vendor:VendorsList'),
                    reverse('vendor:VendorDetails', kwargs={'pk': pk}))
