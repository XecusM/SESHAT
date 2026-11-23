from django.urls import path

from . import views

# application name
app_name = 'vendor'

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
    # Create new vendor
    path('new/', views.NewVendor.as_view(), name='NewVendor'),
    # Edit existing vendor
    path('edit/<int:pk>/', views.EditVendor.as_view(), name='EditVendor'),
    # View existing vendor details
    path('<int:pk>/', views.VendorDetails.as_view(), name='VendorDetails'),
    # Vendors list
    path('list/', views.VendorsList.as_view(), name='VendorsList'),
    # Delete vendor
    path('delete/<int:pk>/', views.delete_vendor, name='DeleteVendor'),
]
