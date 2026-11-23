from django.urls import path

from ..views import locations as views

# patterns
urlpatterns = [
    path('location/new/', views.NewLocation.as_view(), name='NewLocation'),
    path(
        'location/edit/<int:pk>/',
        views.EditLocation.as_view(),
        name='EditLocation'),
    path('locations/', views.LocationsList.as_view(), name='LocationsList'),
    path(
        'location/<int:pk>/',
        views.LocationDetails.as_view(),
        name='LocationDetails'),
    path(
        'location/delete/<int:pk>/',
        views.delete_location,
        name='DeleteLocation'),
    path(
        'sub-location/new/',
        views.NewSubLocation.as_view(),
        name='NewSubLocation'),
    path(
        'sub-location/edit/<int:pk>/',
        views.EditSubLocation.as_view(),
        name='EditSubLocation'),
    path(
        'sub-locations/',
        views.SubLocationsList.as_view(),
        name='SubLocationsList'),
    path(
        'sub-location/<int:pk>/',
        views.SubLocationDetails.as_view(),
        name='SubLocationDetails'),
    path(
        'sub-location/delete/<int:pk>/',
        views.delete_sublocation,
        name='DeleteSubLocation'),
]
