from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from x_django_app.models import XActivity
from x_django_app.views import XListView

from seshat.functools import PaginateMixin, get_next_url

from .. import forms, models


class ItemMixin:
    '''
    Views working on the item sent in the url
    '''

    def get_item(self):
        '''
        Get the item
        '''
        if not hasattr(self, '_item'):
            self._item = get_object_or_404(models.Item, pk=self.kwargs['pk'])
        return self._item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.get_item()
        context['next'] = get_next_url(self.request, '')
        return context

    def get_success_url(self):
        return get_next_url(
                    self.request,
                    reverse('stock:ItemMovesList',
                            kwargs={'pk': self.get_item().pk}))


class NewItemMove(LoginRequiredMixin, UserPassesTestMixin, ItemMixin, FormView):
    '''
    Add or remove a custom quantity of an item
    '''
    template_name = 'stock/moves/move_new.html'
    form_class = forms.ItemMoveForm

    def test_func(self):
        '''
        Check the permission, assembled items can't be moved directly
        '''
        return self.request.user.has_perm('stock.add_itemmove') and \
            not self.get_item().is_assembly

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['item'] = self.get_item()
        return kwargs

    def form_valid(self, form):
        '''
        Save the move and record the activity
        '''
        try:
            move = form.save()
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        XActivity.objects.create_activity(
                        activity_object=move,
                        activity=XActivity.CREATE,
                        user=self.request.user,
                        message=f"Item Move-{move.item.code}/"
                                f"{move.get_type_display()}-{move.id}")
        messages.success(self.request, _('The move has been saved'))
        return HttpResponseRedirect(self.get_success_url())


class NewItemTransfer(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    ItemMixin,
                    FormView):
    '''
    Transfer a quantity of an item from a sub-location to another
    '''
    template_name = 'stock/moves/transfer_new.html'
    form_class = forms.ItemTransferForm

    def test_func(self):
        '''
        Check the permission, assembled items can't be transferred
        '''
        return self.request.user.has_perm('stock.add_itemtransfer') and \
            not self.get_item().is_assembly

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['item'] = self.get_item()
        return kwargs

    def form_valid(self, form):
        '''
        Save the transfer and record the activity
        '''
        try:
            transfer = form.save()
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        XActivity.objects.create_activity(
                        activity_object=transfer,
                        activity=XActivity.CREATE,
                        user=self.request.user,
                        message=f"Item Transfer-{transfer.item.code}")
        messages.success(self.request, _('The transfer has been saved'))
        return HttpResponseRedirect(self.get_success_url())


class ItemMovesList(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    ItemMixin,
                    PaginateMixin,
                    XListView):
    '''
    List of all moves of an item
    '''
    template_name = 'stock/moves/moves_list.html'
    model = models.ItemMove
    search_fields = ['note', 'location__name']
    ordering = ('-created_at', '-id')

    def test_func(self):
        return self.request.user.has_perm('stock.view_item')

    def get_queryset(self):
        '''
        Only the selected item's moves
        '''
        return super().get_queryset().filter(
                        item=self.get_item()).select_related(
                        'location', 'location__location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations_list'] = self.get_item().get_locations()
        return context
