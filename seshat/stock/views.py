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
from stock import forms, models as stock_models

import json
# Create your views here.


class Index(LoginRequiredMixin, TemplateView):
    '''
    View for stock index page
    '''
    template_name = 'stock/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['itemmove_list'] = stock_models.ItemMove.objects.all().order_by('created_at')[:10]
        return context


class CreateCategory(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RCreateView):
    '''
    Create a new category view
    '''
    permission_required = ('stock.add_category',)
    template_name = 'stock/category_new.html'
    model = stock_models.Category
    form_class = forms.CategoryFrom

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Category-{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy('stock:categories_list')


class EditCategory(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RUpdateView):
    '''
    Edit an existing category view
    '''
    permission_required = ('stock.change_category',)
    template_name = 'stock/category_edit.html'
    model = stock_models.Category
    form_class = forms.CategoryFrom

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Category-{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy('stock:categories_list')


class CategoriesList(LoginRequiredMixin, XListView):
    '''
    List of all categories
    '''
    template_name = 'stock/categories_list.html'
    model = stock_models.Category
    search_fields = ['name', ]
    queryset = stock_models.Category.objects.all()
    ordering = ('name', )

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['new_form'] = forms.CategoryFrom
        return context


class CreateLocation(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RCreateView):
    '''
    Create a new location view
    '''
    permission_required = ('stock.add_location',)
    template_name = 'stock/location_new.html'
    model = stock_models.Location
    form_class = forms.LocationForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Location-{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy('stock:locations_list')


class EditLocation(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RUpdateView):
    '''
    Edit an existing location view
    '''
    permission_required = ('stock.change_location',)
    template_name = 'stock/location_edit.html'
    model = stock_models.Location
    form_class = forms.LocationForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Location-{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy('stock:locations_list')


class LocationsList(LoginRequiredMixin, XListView):
    '''
    List of all locations
    '''
    template_name = 'stock/locations_list.html'
    model = stock_models.Location
    search_fields = ['name', ]
    queryset = stock_models.Location.objects.all()
    ordering = ('name', )

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['new_form'] = forms.LocationForm
        return context


class CreateSubLocation(
                        LoginRequiredMixin,
                        PermissionRequiredMixin,
                        RCreateView):
    '''
    Create a new sublocation view
    '''
    permission_required = ('stock.add_sublocation',)
    template_name = 'stock/sublocation_new.html'
    model = stock_models.SubLocation
    form_class = forms.SubLocationForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Sub-Location-{object.location.name}/{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy('stock:sublocations_list')


class EditSubLocation(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    RUpdateView):
    '''
    Edit an existing sublocation view
    '''
    permission_required = ('stock.change_sublocation',)
    template_name = 'stock/sublocation_edit.html'
    model = stock_models.SubLocation
    form_class = forms.SubLocationForm

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Sub-Location-{object.location.name}/{object.name}"

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy('stock:sublocations_list')


class SubLocationsList(LoginRequiredMixin, XListView):
    '''
    List of all sublocations
    '''
    template_name = 'stock/sublocations_list.html'
    model = stock_models.SubLocation
    search_fields = ['name', ]
    queryset = stock_models.SubLocation.objects.all()
    ordering = ('location__name', 'name', )

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['new_form'] = forms.SubLocationForm
        context['locations'] = stock_models.Location.objects.all()
        return context


class CreateItem(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''
    Create a new item view
    '''
    permission_required = ('stock.add_item',)
    template_name = 'stock/item_new.html'

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = forms.ItemForm(request.POST, files=self.request.FILES)

        # check if item is aasembly item
        if 'is_assembly' in request.POST:
            sub_items_data = [{
                'name': f"{i}sub_item",
                'value': int(request.POST[f"{i}sub_item"]),
                'quantity':  int(
                        request.POST[f"{i}quantity"])}  for i in range(
                                        1, int(request.POST['items']) + 1 )]
            sub_items_values = [int(
                        request.POST[f"{i}sub_item"]) for i in range(
                                        1, int(request.POST['items']) + 1 )]
            for i in range(1, int(request.POST['items']) + 1 ):
                if len(
                    list(dict.fromkeys(sub_items_values))
                                                ) != len(sub_items_values):
                    error_message = _("Can't choose the same item twice.")
                    return self.render_to_response(
                                self.get_context_data(
                                            form=form,
                                            error_message=error_message,
                                            assembly='checked',
                                            items=int(request.POST['items']),
                                            sub_items_data=sub_items_data
                                        ))

        if form.is_valid():
            self.object = form.save()
            self.object.created_by = self.request.user
            self.object.save()
            if 'is_assembly' in request.POST:
                self.object.is_assembly = True
                self.object.save()
                for i in range(1, int(request.POST['items']) + 1 ):
                    sub_item = stock_models.Item.objects.get(
                                            id=request.POST[f"{i}sub_item"])
                    stock_models.AssemblyItem.objects.create(
                                        item=self.object,
                                        sub_item=sub_item,
                                        quantity=request.POST[f"{i}quantity"])
            # Store user activity
            activity = Activity.objects.create_activity(
                                    activity_object=self.object,
                                    activity=Activity.CREATE,
                                    user=self.request.user,
                                    message=f"Item-{self.object.code}"
            )
            activity.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            if 'is_assembly' in request.POST:
                return self.render_to_response(self.get_context_data(
                                            form=form,
                                            assembly='checked',
                                            items=int(request.POST['items']),
                                            sub_items_data=sub_items_data
                                        ))
            else:
                return self.render_to_response(self.get_context_data(
                                                                form=form))

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
            context['form'] = forms.ItemForm()

        if 'error_message' in kwargs:
            context['error_message'] = kwargs['error_message']

        if 'assembly' in kwargs:
            context['assembly'] = kwargs['assembly']
            context['items'] = kwargs['items']
            context['sub_items_data'] = json.dumps(kwargs['sub_items_data'])

        context['sub_items'] = json.dumps(
                [item for item in stock_models.Item.objects.filter(
                                        is_active=True
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
                                'stock:item_details',
                                kwargs={'pk': self.object.id})


class EditItem(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''
    Edit an existing item view
    '''
    permission_required = ('stock.change_item',)
    template_name = 'stock/item_edit.html'
    object = None

    def get_object(self):
        '''
        Get the object
        '''
        pk = self.kwargs.get('pk')
        object = self.object = stock_models.Item.objects.get(id=pk)
        return object

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        form = forms.ItemForm(
                            request.POST,
                            files=self.request.FILES,
                            instance=self.object)
        # check if item is aasembly item
        if self.object.is_assembly:
            sub_items_data = [{
                'name': f"{i}sub_item",
                'value': int(request.POST[f"{i}sub_item"]),
                'quantity':  int(
                        request.POST[f"{i}quantity"])}  for i in range(
                                        1, int(request.POST['items']) + 1 )]
            sub_items_values = [int(
                        request.POST[f"{i}sub_item"]) for i in range(
                                        1, int(request.POST['items']) + 1 )]
            for i in range(1, int(request.POST['items']) + 1 ):
                if len(
                    list(dict.fromkeys(sub_items_values))
                                                ) != len(sub_items_values):
                    error_message = _("Can't choose the same item twice.")
                    return self.render_to_response(
                                self.get_context_data(
                                            form=form,
                                            error_message=error_message,
                                            items=int(request.POST['items']),
                                            sub_items_data=sub_items_data
                                        ))

        if form.is_valid():
            self.object = form.save()
            self.object.edited(self.request.user)

            if self.object.is_assembly:
                while int(
                    request.POST['items']
                                ) <= self.object.get_assembly_items().count():
                    removed_item =  self.object.get_assembly_items(
                            )[self.object.get_assembly_items().count() - 1]
                    removed_item.delete()

                for i in range(1, int(request.POST['items']) + 1):
                    sub_item = stock_models.Item.objects.get(
                                            id=request.POST[f"{i}sub_item"])
                    old_sub_items = [
                            item for item in self.object.get_assembly_items(
                                                    ).values(
                                                            'id',
                                                            'quantity', )]
                    if i <= len(old_sub_items):
                        assembly_item = stock_models.AssemblyItem.objects.get(
                                            id=int(old_sub_items[i-1]['id']))
                        assembly_item.sub_item = sub_item
                        assembly_item.quantity = request.POST[f"{i}quantity"]
                        assembly_item.save()
                    else:
                        stock_models.AssemblyItem.objects.create(
                                        item=self.object,
                                        sub_item=sub_item,
                                        quantity=request.POST[f"{i}quantity"])
            # Store user activity
            activity = Activity.objects.create_activity(
                                    activity_object=self.object,
                                    activity=Activity.EDIT,
                                    user=self.request.user,
                                    message=f"Item-{self.object.code}"
            )
            activity.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            if self.object.is_assembly:
                return self.render_to_response(self.get_context_data(
                                            form=form,
                                            items=int(request.POST['items']),
                                            sub_items_data=sub_items_data
                                        ))
            else:
                return self.render_to_response(self.get_context_data(
                                                                form=form))

    def get_context_data(self, form=None, **kwargs):
        '''
        Add more context to template
        '''
        if not self.object:
            self.object = self.get_object()
        context = super().get_context_data()

        context['item'] = self.object

        if self.request.GET.get('next'):
            context['next'] = self.request.GET.get('next')

        if form:
            context['form'] = form
        else:
            context['form'] = forms.ItemForm(instance=self.object)
            if self.object.is_assembly:
                context['items'] = self.object.get_assembly_items().count()
                i = 0
                sub_items_data = list()
                for item in self.object.get_assembly_items():
                    i += 1
                    sub_items_data.append({
                        'name': f"{i}sub_item",
                        'value': item.sub_item.id,
                        'quantity':  item.quantity})
                context['sub_items_data'] = json.dumps(sub_items_data)

        if 'error_message' in kwargs:
            context['error_message'] = kwargs['error_message']

        if 'sub_items_data' in kwargs:
            context['sub_items_data'] = json.dumps(kwargs['sub_items_data'])
            context['items'] = kwargs['items']

        context['sub_items'] = json.dumps(
                [item for item in stock_models.Item.objects.filter(
                                        is_active=True
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
                                'stock:item_details',
                                kwargs={'pk': self.object.id})


class ItemsList(LoginRequiredMixin, XListView):
    '''
    List of all items
    '''
    template_name = 'stock/items_list.html'
    model = stock_models.Item
    search_fields = ['code', 'desciption']
    queryset = stock_models.Item.objects.all()
    ordering = ('code', )

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate

    def post(self, request, *args, **kwargs):
        '''
        add keywords to url in post search
        '''
        redirect_path = request.path_info
        if request.POST['search'] and request.POST['filter']:
            redirect_path += "?search={0}&filter={1}".format(
                                                    request.POST['search'],
                                                    request.POST['filter'])
        elif request.POST['search']:
            redirect_path += "?search={0}".format(request.POST['search'])
        elif request.POST['filter']:
            redirect_path += "?filter={0}".format(request.POST['filter'])

        return HttpResponseRedirect(redirect_path)

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['categories'] = stock_models.Category.objects.all(
                                                        ).order_by('name')
        if self.request.GET.get('filter'):
            context['filter'] = int(self.request.GET.get('filter'))

        return context

    def get_queryset(self):
        '''
        get queryset
        '''
        queryset = super().get_queryset()
        if self.request.GET.get('filter'):
            filter = self.request.GET.get('filter')
            queryset = queryset.filter(category=filter)
        return queryset


class ItemDetails(LoginRequiredMixin, DetailView):
    '''
    View item details
    '''
    template_name = 'stock/item_details.html'
    model = stock_models.Item
    queryset = stock_models.Item.objects.all()


class CreateItemMove(LoginRequiredMixin, UserPassesTestMixin, RCreateView):
    '''
    Create a new item's move view
    '''
    template_name = 'stock/move_new.html'
    model = stock_models.ItemMove
    form_class = forms.ItemMoveForm

    def test_func(self):
        '''
        Check if user has permission and the object is not assembly
        '''
        object = self.get_object()
        return not object.is_assembly and \
                self.request.user.has_perm('stock.add_itemmove')

    def get_object(self):
        '''
        Get the object
        '''
        pk = self.kwargs.get('pk')
        object = self.object = stock_models.Item.objects.get(id=pk)
        return object

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return "Item Move-{0}/{1}-{2}".format(
                                        object.item.code,
                                        object.get_type_display(),
                                        object.id)

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)

        context['item'] = self.get_object()

        context['available_locations'] = json.dumps(
                                            self.get_object().get_locations())
        context['locations'] = json.dumps(
                                [{
                                    'id': location.id,
                                    'name': "{0} / {1}".format(
                                                    location.location.name,
                                                    location.name)
                    } for location in stock_models.SubLocation.objects.all(
                                        ).order_by('location__name', 'name')])

        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        item = self.get_object()
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return reverse_lazy(
                                'stock:moves_list',
                                kwargs={'pk': item.id})


class ItemMovesList(LoginRequiredMixin, XListView):
    '''
    List of all item's moves
    '''
    template_name = 'stock/moves_list.html'
    model = stock_models.ItemMove

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)

        context['item'] = stock_models.Item.objects.get(
                                                    id=self.kwargs.get('pk'))

        return context

    def get_queryset(self):
        '''
        get queryset
        '''
        queryset = super().get_queryset()
        item = stock_models.Item.objects.get(id=self.kwargs.get('pk'))
        queryset = queryset.filter(item=item).order_by('-created_at')
        return queryset


class CreateItemTransfer(
                        LoginRequiredMixin,
                        UserPassesTestMixin,
                        TemplateView):
    '''
    Create a new item's transfer view
    '''
    template_name = 'stock/transfer_new.html'
    model = stock_models.ItemTransfer
    form_class = forms.ItemTransferForm

    def test_func(self):
        '''
        Check if user has permission and the object is not assembly
        '''
        object = self.get_object()
        return not object.is_assembly and \
                self.request.user.has_perm('stock.add_itemtransfer')

    def get_object(self):
        '''
        Get the object
        '''
        pk = self.kwargs.get('pk')
        object = self.object = stock_models.Item.objects.get(id=pk)
        return object

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = forms.ItemTransferForm(request.POST)

        if form.is_valid():
            item = self.get_object()
            old_location = stock_models.SubLocation.objects.get(
                                                id=request.POST['old_location'])
            new_location = stock_models.SubLocation.objects.get(
                                                id=request.POST['new_location'])
            remove_move = stock_models.ItemMove.objects.create(
                                item=item,
                                location=old_location,
                                type=stock_models.ItemMove.REMOVE,
                                quantity=request.POST['quantity'],
                                related_to=stock_models.ItemMove.TRANSFER,
                                created_by=self.request.user)
            add_move = stock_models.ItemMove.objects.create(
                                item=item,
                                location=new_location,
                                type=stock_models.ItemMove.ADD,
                                quantity=request.POST['quantity'],
                                related_to=stock_models.ItemMove.TRANSFER,
                                created_by=self.request.user)
            stock_models.ItemTransfer.objects.create(
                                item=item,
                                old_location=old_location,
                                new_location=new_location,
                                add_move=add_move,
                                remove_move=remove_move)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(
                                                            form=form))

    def get_context_data(self, form=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)

        if form:
            context['form'] = form
        else:
            context['form'] = forms.ItemTransferForm()

        context['item'] = self.get_object()

        context['available_locations'] = json.dumps(
                                            self.get_object().get_locations())

        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        item = stock_models.Item.objects.get(id=self.kwargs.get('pk'))
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return reverse_lazy(
                                'stock:moves_list',
                                kwargs={'pk': item.id})


# Function Views


@login_required
@permission_required('stock.delete_category', raise_exception=True)
def category_delete(request, pk):
    '''
    Delete category
    '''
    if request.method == "POST":
        category = get_object_or_404(stock_models.Category, pk=pk)
        # store user activity
        delete_object = record_delete_object(
                                        request,
                                        category,
                                        f"Category-{category.name}")

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('stock:categories_list')
        else:
            return render(request, 'stock/error_message.html', {
                    'message': _("Couldn't delete the selected category"),
                    'link': reverse('stock:categories_list')})
    else:
        raise Http404


@login_required
@permission_required('stock.delete_location', raise_exception=True)
def location_delete(request, pk):
    '''
    Delete location
    '''
    if request.method == "POST":
        location = get_object_or_404(stock_models.Location, pk=pk)
        # store user activity
        delete_object = record_delete_object(
                                        request,
                                        location,
                                        f"Location-{location.name}")

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('stock:locations_list')
        else:
            return render(request, 'stock/error_message.html', {
                    'message': _("Couldn't delete the selected location"),
                    'link': reverse('stock:locations_list')})
    else:
        raise Http404


@login_required
@permission_required('stock.delete_sublocation', raise_exception=True)
def sublocation_delete(request, pk):
    '''
    Delete sub-location
    '''
    if request.method == "POST":
        sublocation = get_object_or_404(stock_models.SubLocation, pk=pk)
        # store user activity
        delete_object = record_delete_object(
                                        request,
                                        sublocation,
                                        "Sub-Location-{0}/{1}".format(
                                                    sublocation.location.name,
                                                    sublocation.name))

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('stock:sublocations_list')
        else:
            return render(request, 'stock/error_message.html', {
                    'message': _("Couldn't delete the selected sub-location"),
                    'link': reverse('stock:sublocations_list')})
    else:
        raise Http404


@login_required
@permission_required('stock.delete_item', raise_exception=True)
def item_delete(request, pk):
    '''
    Delete item
    '''
    if request.method == "POST":
        item = get_object_or_404(stock_models.Item, pk=pk)
        # store user activity
        delete_object = record_delete_object(
                                            request,
                                            item,
                                            f"Item-{item.code}")

        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('stock:items_list')
        else:
            return render(request, 'stock/error_message.html', {
                    'message': _("Couldn't delete the selected item"),
                    'link': reverse('stock:items_list')})
    else:
        raise Http404
