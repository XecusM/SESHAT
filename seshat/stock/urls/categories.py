from django.urls import path

from ..views import categories as views

# patterns
urlpatterns = [
    path('category/new/', views.NewCategory.as_view(), name='NewCategory'),
    path(
        'category/edit/<int:pk>/',
        views.EditCategory.as_view(),
        name='EditCategory'),
    path('categories/', views.CategoriesList.as_view(), name='CategoriesList'),
    path(
        'category/<int:pk>/',
        views.CategoryDetails.as_view(),
        name='CategoryDetails'),
    path(
        'category/delete/<int:pk>/',
        views.delete_category,
        name='DeleteCategory'),
]
