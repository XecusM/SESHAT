from django.urls import path

from . import views

# applicaton name
app_name = 'vendor'

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
    # Create new vendor
    path(
        'new/<int:pk>/',
        views.CreateVendor.as_view(),
        name='vendor_new'),
    # Edit existing vendor
    path(
        'edit/<int:pk>/',
        views.EditVendor.as_view(),
        name='vendor_edit'),
    # View existing vendor details
    path(
        '<int:pk>/',
        views.VendorDetails.as_view(),
        name='vendor_details'),
    # Vendors list
    path(
        'list/',
        views.VendorsList.as_view(),
        name='vendors_list'),
    # Delete vendor
    path(
        'delete/<int:pk>/',
        views.vendor_delete,
        name='vendor_delete'),
]
