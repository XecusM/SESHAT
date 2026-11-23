from django.urls import path

from ..views import items as views

# patterns
urlpatterns = [
    path('item/new/', views.NewItem.as_view(), name='NewItem'),
    path('item/edit/<int:pk>/', views.EditItem.as_view(), name='EditItem'),
    path('items/', views.ItemsList.as_view(), name='ItemsList'),
    path('item/<int:pk>/', views.ItemDetails.as_view(), name='ItemDetails'),
    path('item/delete/<int:pk>/', views.delete_item, name='DeleteItem'),
]
