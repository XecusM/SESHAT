from django.urls import path

from ..views import moves as views

# patterns
urlpatterns = [
    path('move/new/<int:pk>/', views.NewItemMove.as_view(), name='NewItemMove'),
    path('moves/<int:pk>/', views.ItemMovesList.as_view(), name='ItemMovesList'),
    path(
        'transfer/new/<int:pk>/',
        views.NewItemTransfer.as_view(),
        name='NewItemTransfer'),
]
