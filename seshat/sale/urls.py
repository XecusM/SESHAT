from django.urls import path

from . import views

# applicaton name
app_name = 'sale'

 # patterns
urlpatterns = [
    # Orders list
    path(
        'orders/',
        views.OrdersList.as_view(),
        name='orders_list'),
    # Create new order
    path(
        'order/new/',
        views.CreateOrder.as_view(),
        name='order_new'),
    # Edit existing order
    path(
        'order/edit/<int:pk>/',
        views.EditOrder.as_view(),
        name='order_edit'),
    # View existing order details
    path(
        'order/<int:pk>/',
        views.OrderDetails.as_view(),
        name='order_details'),
    # Delete order
    path(
        'order/delete/<int:pk>/',
        views.order_delete,
        name='order_delete'),
]
