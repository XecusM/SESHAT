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
from sale import forms, models as sales_models
from stock import models as stock_models
from stock import forms as stock_forms

import json
# Create your views here.


class CreateOrder(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''
    Create a new order view
    '''
    permission_required = ('sale.add_saleorder',)
    template_name = 'sale/order_new.html'

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = forms.OrderForm(request.POST)

        items_data = [{
            'name': f"{i}item",
            'value': int(request.POST[f"{i}item"]),
            'quantity':  int(request.POST[f"{i}quantity"]),
            'note': request.POST[f"{i}note"]}  for i in range(
                                    1, int(request.POST['items_count']) + 1 )]
        items_values = [int(
                    request.POST[f"{i}item"]) for i in range(
                                    1, int(request.POST['items_count']) + 1 )]
        for i in range(1, int(request.POST['items_count']) + 1 ):
            if len(
                list(dict.fromkeys(items_values))
                                            ) != len(items_values):
                error_message = _("Can't choose the same item twice.")
                return self.render_to_response(
                            self.get_context_data(
                                form=form,
                                error_message=error_message,
                                items_count=int(request.POST['items_count']),
                                items_data=items_data))
            item = stock_models.Item.objects.get(
                                    id=request.POST[f"{i}item"])
            if item.is_assembly:
                for sub_item in item.get_assembly_items():
                    item_form = stock_forms.ItemMoveForm(data={
                                'item': sub_item.sub_item.id,
                                'type': 'R',
                                'location': sub_item.sub_item.location.id,
                                'quantity': int(
                                        request.POST[f"{i}quantity"]
                                        ) * sub_item.quantity, })
                    if not item_form.is_valid():
                        error_message = item_form.errors
                        return self.render_to_response(
                                    self.get_context_data(
                                        form=form,
                                        error_message=error_message,
                                        items_count=int(
                                                request.POST['items_count']),
                                        items_data=items_data))
            else:
                item_form = stock_forms.ItemMoveForm(data={
                                    'item': item.id,
                                    'type': 'R',
                                    'location': item.location.id,
                                    'quantity': int(
                                                request.POST[f"{i}quantity"]),
                                    'note': request.POST[f"{i}note"]})
                if not item_form.is_valid():
                    error_message = item_form.errors
                    return self.render_to_response(
                                self.get_context_data(
                                    form=form,
                                    error_message=error_message,
                                    items_count=int(
                                                request.POST['items_count']),
                                    items_data=items_data))

        if form.is_valid():
            self.object = form.save()
            self.object.created_by = self.request.user
            self.object.save()

            for i in range(1, int(request.POST['items_count']) + 1 ):
                item = stock_models.Item.objects.get(
                                        id=request.POST[f"{i}item"])
                item_move = stock_models.ItemMove.objects.create(
                                    item=item,
                                    location=item.location,
                                    type=stock_models.ItemMove.REMOVE,
                                    related_to=stock_models.ItemMove.SELL,
                                    quantity=request.POST[f"{i}quantity"])

                sales_models.SaleItems.objects.create(
                                    order=self.object,
                                    item=item_move,
                                    price=item.price,
                                    note=request.POST[f"{i}note"],
                )
            # Store user activity
            activity = Activity.objects.create_activity(
                            activity_object=self.object,
                            activity=Activity.CREATE,
                            user=self.request.user,
                            message="Sale Order-{0}/{1}".format(
                                                    self.object.company.name,
                                                    self.object.id)
            )
            activity.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(
                                form=form,
                                items_count=int(request.POST['items_count']),
                                items_data=items_data
                            ))

    def get_context_data(self, form=None, **kwargs):
        '''
        Add more context to template
        '''
        context = super().get_context_data()
        if self.request.GET.get('next'):
            context['next'] = self.request.GET.get('next')

        if form:
            context['form'] = form
        else:
            context['form'] = forms.OrderForm()

        if 'error_message' in kwargs:
            context['error_message'] = kwargs['error_message']

        if 'items_count' in kwargs:
            context['items_count'] = kwargs['items_count']
            context['items_data'] = json.dumps(kwargs['items_data'])

        context['items'] = json.dumps(
                [{
                'id': item.id,
                'code': item.code,
                'desciption': item.desciption,
                'total_quantity': item.quantity,
                'available_quantity': item.get_quantity(item.location)
                } for item in stock_models.Item.objects.filter(
                                                            is_active=True,
                                                        ).order_by('code')])

        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return reverse_lazy(
                                'sale:order_details',
                                kwargs={'pk': self.object.id})


class EditOrder(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''
    Edit an existing order view
    '''
    permission_required = ('sale.change_saleorder',)
    template_name = 'sale/order_edit.html'
    object = None

    def get_object(self):
        '''
        Get the object
        '''
        pk = self.kwargs.get('pk')
        self.object = sales_models.SaleOrder.objects.get(id=pk)
        return self.object

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        form = forms.OrderForm(request.POST, instance=self.object)
        items_data = [{
            'name': f"{i}item",
            'value': int(request.POST[f"{i}item"]),
            'quantity':  int(request.POST[f"{i}quantity"]),
            'note': request.POST[f"{i}note"]}  for i in range(
                                    1, int(request.POST['items_count']) + 1 )]
        items_values = [int(
                    request.POST[f"{i}item"]) for i in range(
                                    1, int(request.POST['items_count']) + 1 )]
        for i in range(1, int(request.POST['items_count']) + 1 ):
            if len(
                list(dict.fromkeys(items_values))
                                            ) != len(items_values):
                error_message = _("Can't choose the same item twice.")
                return self.render_to_response(
                            self.get_context_data(
                                form=form,
                                error_message=error_message,
                                items_count=int(request.POST['items_count']),
                                items_data=items_data))
            item = stock_models.Item.objects.get(
                                    id=request.POST[f"{i}item"])
            if item.is_assembly:
                for sub_item in item.get_assembly_items():
                    item_form = stock_forms.ItemMoveForm(data={
                                'item': sub_item.sub_item.id,
                                'type': 'R',
                                'location': sub_item.sub_item.location.id,
                                'quantity': int(
                                        request.POST[f"{i}quantity"]
                                        ) * sub_item.quantity, })
                    if not item_form.is_valid():
                        error_message = item_form.errors
                        return self.render_to_response(
                                    self.get_context_data(
                                        form=form,
                                        error_message=error_message,
                                        items_count=int(
                                                request.POST['items_count']),
                                        items_data=items_data))
            else:
                item_form = stock_forms.ItemMoveForm(data={
                                    'item': item.id,
                                    'type': 'R',
                                    'location': item.location.id,
                                    'quantity': int(
                                                request.POST[f"{i}quantity"]),
                                    'note': request.POST[f"{i}note"]})
                if not item_form.is_valid():
                    error_message = item_form.errors
                    return self.render_to_response(
                                self.get_context_data(
                                    form=form,
                                    error_message=error_message,
                                    items_count=int(
                                                request.POST['items_count']),
                                    items_data=items_data))

        if form.is_valid():
            self.object = form.save()
            self.object.edited(self.request.user)

            while int(
                request.POST['items_count']
                            ) < self.object.get_items().count():
                removed_item =  self.object.get_items(
                        )[self.object.get_items().count() - 1]
                removed_item.delete()

            for i in range(1, int(request.POST['items_count']) + 1):
                item = stock_models.Item.objects.get(
                                                id=request.POST[f"{i}item"])
                old_items = [
                        item for item in self.object.get_items(
                                                ).values('id')]
                if i <= len(old_items):
                    sale_item = sales_models.SaleItems.objects.get(
                                        id=int(old_items[i-1]['id']))
                    sale_item.item.item = item
                    sale_item.item.quantity = request.POST[f"{i}quantity"]
                    sale_item.note = request.POST[f"{i}note"]
                    sale_item.item.save()
                    sale_item.save()
                else:
                    item_move = stock_models.ItemMove.objects.create(
                                        item=item,
                                        location=item.location,
                                        type=stock_models.ItemMove.REMOVE,
                                        related_to=stock_models.ItemMove.SELL,
                                        quantity=request.POST[f"{i}quantity"])
                    sales_models.SaleItems.objects.create(
                                    order=self.object,
                                    item=item_move,
                                    price=item.price,
                                    note=request.POST[f"{i}note"],
                    )
            # Store user activity
            activity = Activity.objects.create_activity(
                            activity_object=self.object,
                            activity=Activity.EDIT,
                            user=self.request.user,
                            message="Sale Order-{0}/{1}".format(
                                                    self.object.company.name,
                                                    self.object.id)
            )
            activity.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(
                                form=form,
                                items_count=int(request.POST['items_count']),
                                items_data=items_data
                            ))

    def get_context_data(self, form=None, **kwargs):
        '''
        Add more context to template
        '''
        if not self.object:
            self.object = self.get_object()
        context = super().get_context_data()

        context['saleorder'] = self.object

        if self.request.GET.get('next'):
            context['next'] = self.request.GET.get('next')

        if form:
            context['form'] = form
        else:
            context['form'] = forms.OrderForm(instance=self.object)
            i = 0
            items_data = list()
            for item in self.object.get_items():
                i += 1
                items_data.append({
                    'name': f"{i}item",
                    'value': item.item.item.id,
                    'quantity':  item.item.quantity,
                    'note': item.note})
            context['items_data'] = json.dumps(items_data)
            context['items_count'] = self.object.get_items().count()

        if 'error_message' in kwargs:
            context['error_message'] = kwargs['error_message']

        if 'items_count' in kwargs:
            context['items_count'] = kwargs['items_count']
            context['items_data'] = json.dumps(kwargs['items_data'])

        context['items'] = json.dumps(
                [item for item in stock_models.Item.objects.filter(
                                        is_active=True,
                                    ).order_by('code').values(
                                                            'id',
                                                            'code',
                                                            'desciption', )])
        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return reverse_lazy(
                                'sale:order_details',
                                kwargs={'pk': self.object.id})


class OrdersList(LoginRequiredMixin, XListView):
    '''
    List of all orders
    '''
    template_name = 'sale/orders_list.html'
    model = sales_models.SaleOrder
    search_fields = ['company__name', 'invoice', 'note', ]
    queryset = sales_models.SaleOrder.objects.all()
    ordering = ('-created_at',)

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class OrderDetails(LoginRequiredMixin, DetailView):
    '''
    View order details
    '''
    template_name = 'sale/order_details.html'
    model = sales_models.SaleOrder
    queryset = sales_models.SaleOrder.objects.all()

# Function Views


@login_required
@permission_required('sale.delete_saleorder', raise_exception=True)
def order_delete(request, pk):
    '''
    Delete order
    '''
    if request.method == "POST":
        order = get_object_or_404(sales_models.SaleOrder, pk=pk)
        # store user activity
        activity = Activity.objects.create_activity(
                            activity_object=order,
                            activity=Activity.DELETE,
                            user=request.user,
                            message=f"Order-{order.id}-{order.company.name}"
        )
        activity.save()
        try:
            with transaction.atomic():
                order.delete()
        except Exception as error_type:
            activity.delete()
            return render(request, 'sale/error_message.html', {
                    'message': _("Couldn't delete the selected order"),
                    'link': reverse('sale:orders_list')})
    else:
        raise Http404

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    else:
        return redirect('sale:orders_list')
