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
    permission_required = ('customer.add_customercompany',)
    template_name = 'customer/company_new.html'
    model = models.CustomerCompany
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
    permission_required = ('customer.change_customercompany',)
    template_name = 'customer/company_edit.html'
    model = models.CustomerCompany
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
    permission_required = ('customer.view_customercompany',)
    template_name = 'customer/companies_list.html'
    model = models.CustomerCompany
    search_fields = ['name', 'description', 'phone', 'tax_code']
    queryset = models.CustomerCompany.objects.all()
    ordering = ('name', )


class CompanyDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View company details
    '''
    permission_required = ('customer.view_customercompany',)
    template_name = 'customer/company_details.html'
    model = models.CustomerCompany


class NewCustomer(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                NextUrlMixin,
                XCreateView):
    '''
    Create a new customer view
    '''
    permission_required = ('customer.add_customer',)
    template_name = 'customer/customer_new.html'
    model = models.Customer
    form_class = forms.CustomerForm

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
        return f"Customer-{object.company.name}-{object.full_name}"


class EditCustomer(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                NextUrlMixin,
                XUpdateView):
    '''
    Edit an existing customer view
    '''
    permission_required = ('customer.change_customer',)
    template_name = 'customer/customer_edit.html'
    model = models.Customer
    form_class = forms.CustomerForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Customer-{object.company.name}-{object.full_name}"


class CustomersList(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    PaginateMixin,
                    XListView):
    '''
    List of all customers
    '''
    permission_required = ('customer.view_customer',)
    template_name = 'customer/customers_list.html'
    model = models.Customer
    search_fields = [
                    'first_name', 'last_name', 'email',
                    'phone', 'company__name']
    queryset = models.Customer.objects.select_related('company')
    ordering = ('first_name', 'last_name')


class CustomerDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View customer details
    '''
    permission_required = ('customer.view_customer',)
    template_name = 'customer/customer_details.html'
    model = models.Customer


# Function Views


@login_required
@permission_required('customer.delete_customercompany', raise_exception=True)
@require_POST
def delete_company(request, pk):
    '''
    Delete company
    '''
    return delete_object(
                    request,
                    models.CustomerCompany,
                    pk,
                    lambda company: f"Company-{company.name}",
                    reverse('customer:CompaniesList'),
                    reverse('customer:CompanyDetails', kwargs={'pk': pk}))


@login_required
@permission_required('customer.delete_customer', raise_exception=True)
@require_POST
def delete_customer(request, pk):
    '''
    Delete customer
    '''
    return delete_object(
                    request,
                    models.Customer,
                    pk,
                    lambda customer: "Customer-{0}-{1}".format(
                                                customer.company.name,
                                                customer.full_name),
                    reverse('customer:CustomersList'),
                    reverse('customer:CustomerDetails', kwargs={'pk': pk}))
