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
from customer import forms, models as customers_models

# Create your views here.


class CreateCompany(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RCreateView):
    '''
    Create a new company view
    '''
    permission_required = ('customer.add_customercompany',)
    template_name = 'customer/company_new.html'
    model = customers_models.CustomerCompany
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
                                'customer:company_details',
                                kwargs={'pk': self.object.pk})


class EditCompany(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RUpdateView):
    '''
    Edit an existing company view
    '''
    permission_required = ('customer.change_customercompany',)
    template_name = 'customer/company_edit.html'
    model = customers_models.CustomerCompany
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
                                'customer:company_details',
                                kwargs={'pk': self.object.pk})


class CompaniesList(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    List of all companies
    '''
    permission_required = ('customer.view_customercompany',)
    template_name = 'customer/companies_list.html'
    model = customers_models.CustomerCompany
    search_fields = ['name', 'desciption', 'phone']
    queryset = customers_models.CustomerCompany.objects.all()
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
    permission_required = ('customer.view_customercompany',)
    template_name = 'customer/company_details.html'
    model = customers_models.CustomerCompany
    queryset = customers_models.CustomerCompany.objects.all()


class CreateCustomer(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RCreateView):
    '''
    Create a new customer view
    '''
    permission_required = ('customer.add_customer',)
    template_name = 'customer/customer_new.html'
    model = customers_models.Customer
    form_class = forms.CustomerForm

    def get_context_data(self, **kwargs):
        '''
        add extra context to template
        '''
        context = super().get_context_data(**kwargs)
        context['company'] = customers_models.CustomerCompany.objects.get(
                                                    id=self.kwargs['pk'])
        return context

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return "Customer-{0}-{1}".format(
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
                                'customer:customer_details',
                                kwargs={'pk': self.object.pk})


class EditCustomer(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RUpdateView):
    '''
    Edit an existing customer view
    '''
    permission_required = ('customer.change_customer',)
    template_name = 'customer/customer_edit.html'
    model = customers_models.Customer
    form_class = forms.CustomerForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return "Customer-{0}-{1}".format(
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
                                'customer:customer_details',
                                kwargs={'pk': self.object.pk})


class CustomersList(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    List of all customers
    '''
    permission_required = ('customer.view_customer',)
    template_name = 'customer/customers_list.html'
    model = customers_models.Customer
    search_fields = ['first_name', 'last_name', ]
    queryset = customers_models.Customer.objects.all()
    ordering = ('first_name', 'last_name')

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class CustomerDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View customer details
    '''
    permission_required = ('customer.view_customer',)
    template_name = 'customer/customer_details.html'
    model = customers_models.Customer
    queryset = customers_models.Customer.objects.all()


# Function Views


@login_required
@permission_required('customer.delete_customercompany', raise_exception=True)
def company_delete(request, pk):
    '''
    Delete company
    '''
    if request.method == "POST":
        company = get_object_or_404(customers_models.CustomerCompany, pk=pk)
        # store user activity
        delete_object = record_delete_object(
                                        request,
                                        company,
                                        f"Company-{company.name}")

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('customer:companies_list')
        else:
            return render(request, 'customer/error_message.html', {
                    'message': _("Couldn't delete the selected company"),
                    'link': reverse('customer:companies_list')})
    else:
        raise Http404


@login_required
@permission_required('customer.delete_customer', raise_exception=True)
def customer_delete(request, pk):
    '''
    Delete customer
    '''
    if request.method == "POST":
        customer = get_object_or_404(customers_models.Customer, pk=pk)
        # store user activity
        delete_object =  record_delete_object(
                                        request,
                                        customer,
                                        "Customer-{0}-{1}".format(
                                                    customer.company.name,
                                                    customer.full_name))

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('customer:customers_list')
        else:
            return render(request, 'customer/error_message.html', {
                    'message': _("Couldn't delete the selected customer"),
                    'link': reverse('customer:customers_list')})
    else:
        raise Http404
