from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

import json

from x_django_app.models import XActivity
from x_django_app.views import XListView

from seshat.functools import PaginateMixin, delete_object, get_next_url

from . import forms, models

# Create your views here.


class OrderFormMixin:
    '''
    Shared logic of the new and edit order views: the order form and the
    order lines formset
    '''
    object = None

    def get_initial_lines(self):
        '''
        The lines of the edited order
        '''
        if self.object is None:
            return [{}]
        return [{
                    'item': line.item.item_id,
                    'quantity': line.item.quantity,
                    'price': line.price,
                    'note': line.note,
                } for line in self.object.get_items()]

    def get_forms(self):
        '''
        Build the order form and the lines formset
        '''
        if self.request.method == 'POST':
            form = forms.OrderForm(self.request.POST, instance=self.object)
            formset = forms.OrderLineFormSet(self.request.POST, prefix='lines')
        else:
            form = forms.OrderForm(instance=self.object)
            formset = forms.OrderLineFormSet(
                                    initial=self.get_initial_lines(),
                                    prefix='lines')
        return form, formset

    def get(self, request, *args, **kwargs):
        form, formset = self.get_forms()
        return self.render_to_response(
                    self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        form, formset = self.get_forms()
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    self.object.set_items(formset.get_lines())
            except ValidationError as error:
                if self.activity == XActivity.CREATE:
                    self.object = None
                form.add_error(None, error)
            else:
                XActivity.objects.create_activity(
                            activity_object=self.object,
                            activity=self.activity,
                            user=request.user,
                            message=f"{self.message_name}-"
                                    f"{self.object.company.name}/"
                                    f"{self.object.id}")
                messages.success(request, self.success_message)
                return HttpResponseRedirect(get_next_url(
                                    request, self.object.get_absolute_url()))
        return self.render_to_response(
                    self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = get_next_url(self.request, '')
        context['order'] = self.object
        context['items_data'] = json.dumps({
            str(item.id): {
                'price': str(item.price),
                'quantity': item.quantity,
                'description': item.description or '',
            } for item in forms.ITEMS_QUERYSET()})
        return context


class NewOrder(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                OrderFormMixin,
                TemplateView):
    '''
    Create a new order view
    '''
    permission_required = ('sale.add_saleorder',)
    template_name = 'sale/order_new.html'
    activity = XActivity.CREATE
    message_name = 'Sale Order'
    success_message = _('The order has been created')


class EditOrder(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                OrderFormMixin,
                TemplateView):
    '''
    Edit an existing order view
    '''
    permission_required = ('sale.change_saleorder',)
    template_name = 'sale/order_edit.html'
    activity = XActivity.EDIT
    message_name = 'Sale Order'
    success_message = _('The order has been updated')

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(models.SaleOrder, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class OrdersList(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                PaginateMixin,
                XListView):
    '''
    List of all orders
    '''
    permission_required = ('sale.view_saleorder',)
    template_name = 'sale/orders_list.html'
    model = models.SaleOrder
    search_fields = ['company__name', 'invoice', 'note', ]
    queryset = models.SaleOrder.objects.select_related('company')
    ordering = ('-created_at', '-id')

    def get_queryset(self):
        '''
        Filter by date range
        '''
        queryset = super().get_queryset()
        if self.request.GET.get('from_date'):
            queryset = queryset.filter(
                    created_at__date__gte=self.request.GET.get('from_date'))
        if self.request.GET.get('to_date'):
            queryset = queryset.filter(
                    created_at__date__lte=self.request.GET.get('to_date'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        return context


class OrderDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View order details
    '''
    permission_required = ('sale.view_saleorder',)
    template_name = 'sale/order_details.html'
    model = models.SaleOrder
    context_object_name = 'order'


# Function Views


@login_required
@permission_required('sale.delete_saleorder', raise_exception=True)
@require_POST
def delete_order(request, pk):
    '''
    Delete order
    '''
    return delete_object(
                    request,
                    models.SaleOrder,
                    pk,
                    lambda order: f"Sale Order-{order.company.name}/{order.id}",
                    reverse('sale:OrdersList'),
                    reverse('sale:OrderDetails', kwargs={'pk': pk}))
