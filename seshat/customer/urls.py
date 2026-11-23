from django.urls import path

from . import views

# application name
app_name = 'customer'

# patterns
urlpatterns = [
    # Create new company
    path('company/new/', views.NewCompany.as_view(), name='NewCompany'),
    # Edit existing company
    path(
        'company/edit/<int:pk>/',
        views.EditCompany.as_view(),
        name='EditCompany'),
    # View existing company details
    path(
        'company/<int:pk>/',
        views.CompanyDetails.as_view(),
        name='CompanyDetails'),
    # Companies list
    path('companies/', views.CompaniesList.as_view(), name='CompaniesList'),
    # Delete company
    path(
        'company/delete/<int:pk>/',
        views.delete_company,
        name='DeleteCompany'),
    # Create new customer
    path('new/', views.NewCustomer.as_view(), name='NewCustomer'),
    # Edit existing customer
    path('edit/<int:pk>/', views.EditCustomer.as_view(), name='EditCustomer'),
    # View existing customer details
    path('<int:pk>/', views.CustomerDetails.as_view(), name='CustomerDetails'),
    # Customers list
    path('list/', views.CustomersList.as_view(), name='CustomersList'),
    # Delete customer
    path('delete/<int:pk>/', views.delete_customer, name='DeleteCustomer'),
]
