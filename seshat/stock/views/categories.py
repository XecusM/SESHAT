from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from x_django_app.views import XCreateView, XUpdateView, XListView

from seshat.functools import PaginateMixin, NextUrlMixin, delete_object

from .. import forms, models


class NewCategory(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    NextUrlMixin,
                    XCreateView):
    '''
    Create a new category view
    '''
    permission_required = ('stock.add_category',)
    template_name = 'stock/categories/category_new.html'
    model = models.Category
    form_class = forms.CategoryForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Category-{object.name}"

    def get_default_success_url(self):
        return reverse('stock:CategoryDetails', kwargs={'pk': self.object.pk})


class EditCategory(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    NextUrlMixin,
                    XUpdateView):
    '''
    Edit an existing category view
    '''
    permission_required = ('stock.change_category',)
    template_name = 'stock/categories/category_edit.html'
    model = models.Category
    form_class = forms.CategoryForm

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Category-{object.name}"

    def get_default_success_url(self):
        return reverse('stock:CategoryDetails', kwargs={'pk': self.object.pk})


class CategoriesList(
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    PaginateMixin,
                    XListView):
    '''
    List of all categories
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/categories/categories_list.html'
    model = models.Category
    search_fields = ['name', ]
    queryset = models.Category.objects.all()
    ordering = ('name', )


class CategoryDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View category details and its items
    '''
    permission_required = ('stock.view_item',)
    template_name = 'stock/categories/category_details.html'
    model = models.Category


@login_required
@permission_required('stock.delete_category', raise_exception=True)
@require_POST
def delete_category(request, pk):
    '''
    Delete category
    '''
    return delete_object(
                    request,
                    models.Category,
                    pk,
                    lambda category: f"Category-{category.name}",
                    reverse('stock:CategoriesList'))
