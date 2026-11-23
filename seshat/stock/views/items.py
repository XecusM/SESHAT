from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

from x_django_app.models import XActivity
from x_django_app.views import XListView

from seshat.functools import (
                            PaginateMixin, delete_object, get_next_url, )

from .. import forms, models


class Index(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''
    Stock dashboard
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/index.html'

    def get_context_data(self, **kwargs):
        '''
        Stock figures, low stock items and the latest moves
        '''
        context = super().get_context_data(**kwargs)
        items = list(models.Item.objects.filter(is_active=True))
        context['items_count'] = len(items)
        context['low_stock_list'] = [
                                item for item in items if item.is_low_stock]
        context['stock_value'] = sum(
                    (item.stock_value for item in items
                     if not item.is_assembly), 0)
        context['categories_list'] = models.Category.objects.annotate(
                    items_count=Count('item_category')).order_by(
                    '-items_count')[:8]
        context['locations_count'] = models.SubLocation.objects.count()
        context['itemmove_list'] = models.ItemMove.objects.select_related(
                    'item', 'location', 'location__location').exclude(
                    related_to=models.ItemMove.ASSEMBLY)[:10]
        return context


class ItemFormMixin:
    '''
    Shared logic of the new and edit item views: the item form and the
    components formset of an assembled item
    '''
    object = None

    def get_forms(self):
        '''
        Build the item form and the components formset
        '''
        data = self.request.POST if self.request.method == 'POST' else None
        files = self.request.FILES if self.request.method == 'POST' else None
        form = forms.ItemForm(data, files, instance=self.object)
        formset = forms.AssemblyItemFormSet(
                                    data,
                                    instance=self.object or models.Item(),
                                    prefix='components')
        return form, formset

    def is_assembly(self, form):
        '''
        Whether the posted item is an assembled item
        '''
        if self.object is not None:
            return self.object.is_assembly
        return bool(form.cleaned_data.get('is_assembly'))

    def get(self, request, *args, **kwargs):
        form, formset = self.get_forms()
        return self.render_to_response(
                    self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        form, formset = self.get_forms()
        if form.is_valid():
            assembly = self.is_assembly(form)
            if not assembly or formset.is_valid():
                try:
                    with transaction.atomic():
                        self.object = form.save()
                        if assembly:
                            formset.instance = self.object
                            formset.save()
                except ValidationError as error:
                    form.add_error(None, error)
                else:
                    XActivity.objects.create_activity(
                                activity_object=self.object,
                                activity=self.activity,
                                user=request.user,
                                message=f"Item-{self.object.code}")
                    messages.success(request, self.success_message)
                    return HttpResponseRedirect(get_next_url(
                        request,
                        reverse('stock:ItemDetails',
                                kwargs={'pk': self.object.pk})))
        return self.render_to_response(
                    self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = get_next_url(self.request, '')
        context['item'] = self.object
        return context


class NewItem(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                ItemFormMixin,
                TemplateView):
    '''
    Create a new item (normal or assembled)
    '''
    permission_required = ('stock.add_item',)
    template_name = 'stock/items/item_new.html'
    activity = XActivity.CREATE
    success_message = _('The item has been created')


class EditItem(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                ItemFormMixin,
                TemplateView):
    '''
    Edit an existing item
    '''
    permission_required = ('stock.change_item',)
    template_name = 'stock/items/item_edit.html'
    activity = XActivity.EDIT
    success_message = _('The item has been updated')

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(models.Item, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class ItemsList(
                LoginRequiredMixin,
                PermissionRequiredMixin,
                PaginateMixin,
                XListView):
    '''
    List of all items
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/items/items_list.html'
    model = models.Item
    search_fields = ['code', 'description', 'barcode']
    queryset = models.Item.objects.select_related(
                                    'category', 'location', 'location__location')
    ordering = ('code', )

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['categories'] = models.Category.objects.order_by('name')
        context['category'] = self.request.GET.get('category', '')
        context['status'] = self.request.GET.get('status', '')
        return context

    def get_queryset(self):
        '''
        Filter by category and status
        '''
        queryset = super().get_queryset()
        category = self.request.GET.get('category', '')
        if category.isdigit():
            queryset = queryset.filter(category=category)
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'disabled':
            queryset = queryset.filter(is_active=False)
        elif status == 'assembly':
            queryset = queryset.filter(is_assembly=True)
        elif status == 'low':
            ids = [item.id for item in queryset if item.is_low_stock]
            queryset = queryset.filter(id__in=ids)
        return queryset


class ItemDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View item details
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/items/item_details.html'
    model = models.Item
    queryset = models.Item.objects.select_related(
                                    'category', 'location', 'location__location')

    def get_context_data(self, **kwargs):
        '''
        Latest moves of the item
        '''
        context = super().get_context_data(**kwargs)
        context['moves_list'] = self.object.get_item_moves().select_related(
                                    'location', 'location__location')[:10]
        return context


@login_required
@permission_required('stock.delete_item', raise_exception=True)
@require_POST
def delete_item(request, pk):
    '''
    Delete item
    '''
    return delete_object(
                    request,
                    models.Item,
                    pk,
                    lambda item: f"Item-{item.code}",
                    reverse('stock:ItemsList'),
                    reverse('stock:ItemDetails', kwargs={'pk': pk}))
