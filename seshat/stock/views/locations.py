from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from x_django_app.views import XCreateView, XUpdateView, XListView

from seshat.functools import PaginateMixin, NextUrlMixin, delete_object

from .. import forms, models


class NewLocation(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    NextUrlMixin,
                    XCreateView):
    '''
    Create a new location view
    '''
    permission_required = ('stock.add_location',)
    template_name = 'stock/locations/location_new.html'
    model = models.Location
    form_class = forms.LocationForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Location-{object.name}"

    def get_default_success_url(self):
        return reverse('stock:LocationDetails', kwargs={'pk': self.object.pk})


class EditLocation(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    NextUrlMixin,
                    XUpdateView):
    '''
    Edit an existing location view
    '''
    permission_required = ('stock.change_location',)
    template_name = 'stock/locations/location_edit.html'
    model = models.Location
    form_class = forms.LocationForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Location-{object.name}"

    def get_default_success_url(self):
        return reverse('stock:LocationDetails', kwargs={'pk': self.object.pk})


class LocationsList(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    PaginateMixin,
                    XListView):
    '''
    List of all locations
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/locations/locations_list.html'
    model = models.Location
    search_fields = ['name', 'sub_location__name']
    queryset = models.Location.objects.prefetch_related('sub_location')
    ordering = ('name', )


class LocationDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View location details and its sub-locations
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/locations/location_details.html'
    model = models.Location


class NewSubLocation(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    NextUrlMixin,
                    XCreateView):
    '''
    Create a new sub-location view
    '''
    permission_required = ('stock.add_sublocation',)
    template_name = 'stock/locations/sublocation_new.html'
    model = models.SubLocation
    form_class = forms.SubLocationForm

    def get_initial(self):
        '''
        Pre-select the location sent in the url
        '''
        initial = super().get_initial()
        if self.request.GET.get('location'):
            initial['location'] = self.request.GET.get('location')
        return initial

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Sub-Location-{object.location.name}/{object.name}"

    def get_default_success_url(self):
        return reverse(
                    'stock:SubLocationDetails', kwargs={'pk': self.object.pk})


class EditSubLocation(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    NextUrlMixin,
                    XUpdateView):
    '''
    Edit an existing sub-location view
    '''
    permission_required = ('stock.change_sublocation',)
    template_name = 'stock/locations/sublocation_edit.html'
    model = models.SubLocation
    form_class = forms.SubLocationForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Sub-Location-{object.location.name}/{object.name}"

    def get_default_success_url(self):
        return reverse(
                    'stock:SubLocationDetails', kwargs={'pk': self.object.pk})


class SubLocationsList(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    PaginateMixin,
                    XListView):
    '''
    List of all sub-locations
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/locations/sublocations_list.html'
    model = models.SubLocation
    search_fields = ['name', 'location__name']
    queryset = models.SubLocation.objects.select_related('location')
    ordering = ('location__name', 'name')

    def get_queryset(self):
        '''
        Filter by location
        '''
        queryset = super().get_queryset()
        if self.request.GET.get('location', '').isdigit():
            queryset = queryset.filter(location=self.request.GET.get('location'))
        return queryset

    def get_context_data(self, **kwargs):
        '''
        Send the locations filter to the template
        '''
        context = super().get_context_data(**kwargs)
        context['locations'] = models.Location.objects.order_by('name')
        context['location'] = self.request.GET.get('location', '')
        return context


class SubLocationDetails(
                        LoginRequiredMixin,
                        PermissionRequiredMixin,
                        DetailView):
    '''
    View sub-location details and the items stored in it
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/locations/sublocation_details.html'
    model = models.SubLocation

    def get_context_data(self, **kwargs):
        '''
        Send the items with their quantity in this sub-location
        '''
        context = super().get_context_data(**kwargs)
        context['items_list'] = [
                (item, item.get_quantity(self.object))
                for item in self.object.get_items()]
        return context


@login_required
@permission_required('stock.delete_location', raise_exception=True)
@require_POST
def delete_location(request, pk):
    '''
    Delete location
    '''
    return delete_object(
                    request,
                    models.Location,
                    pk,
                    lambda location: f"Location-{location.name}",
                    reverse('stock:LocationsList'))


@login_required
@permission_required('stock.delete_sublocation', raise_exception=True)
@require_POST
def delete_sublocation(request, pk):
    '''
    Delete sub-location
    '''
    return delete_object(
                    request,
                    models.SubLocation,
                    pk,
                    lambda sub: f"Sub-Location-{sub.location.name}/{sub.name}",
                    reverse('stock:SubLocationsList'))
