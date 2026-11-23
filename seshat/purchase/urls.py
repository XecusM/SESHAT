from django.urls import path

from . import views

# application name
app_name = 'purchase'

# patterns
urlpatterns = [
    # Orders list
    path('orders/', views.OrdersList.as_view(), name='OrdersList'),
    # Create new order
    path('order/new/', views.NewOrder.as_view(), name='NewOrder'),
    # Edit existing order
    path('order/edit/<int:pk>/', views.EditOrder.as_view(), name='EditOrder'),
    # View existing order details
    path('order/<int:pk>/', views.OrderDetails.as_view(), name='OrderDetails'),
    # Delete order
    path('order/delete/<int:pk>/', views.delete_order, name='DeleteOrder'),
]
