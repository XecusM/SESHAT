from django.urls import path

from . import views

# applicaton name
app_name = 'customer'

 # patterns
urlpatterns = [
    # Create new company
    path(
        'company/new/',
        views.CreateCompany.as_view(),
        name='company_new'),
    # Edit existing company
    path(
        'company/edit/<int:pk>/',
        views.EditCompany.as_view(),
        name='company_edit'),
    # View existing company details
    path(
        'company/<int:pk>/',
        views.CompanyDetails.as_view(),
        name='company_details'),
    # Companies list
    path(
        'companies/',
        views.CompaniesList.as_view(),
        name='companies_list'),
    # Delete company
    path(
        'company/delete/<int:pk>/',
        views.company_delete,
        name='company_delete'),
    # Create new customer
    path(
        'new/<int:pk>/',
        views.CreateCustomer.as_view(),
        name='customer_new'),
    # Edit existing customer
    path(
        'edit/<int:pk>/',
        views.EditCustomer.as_view(),
        name='customer_edit'),
    # View existing customer details
    path(
        '<int:pk>/',
        views.CustomerDetails.as_view(),
        name='customer_details'),
    # Customers list
    path(
        'list/',
        views.CustomersList.as_view(),
        name='customers_list'),
    # Delete customer
    path(
        'delete/<int:pk>/',
        views.customer_delete,
        name='customer_delete'),
]
