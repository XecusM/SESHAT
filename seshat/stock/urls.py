from django.urls import path

from . import views

# applicaton name
app_name = 'stock'

# patterns
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    # Create new category
    path(
        'category/new/',
        views.CreateCategory.as_view(),
        name='category_new'),
    # Edit existing category
    path(
        'category/edit/<int:pk>/',
        views.EditCategory.as_view(),
        name='category_edit'),
    # Categories list
    path(
        'categories/',
        views.CategoriesList.as_view(),
        name='categories_list'),
    # Delete category
    path(
        'category/delete/<int:pk>/',
        views.category_delete,
        name='category_delete'),
    # Create new location
    path(
        'location/new/',
        views.CreateLocation.as_view(),
        name='location_new'),
    # Edit existing location
    path(
        'location/edit/<int:pk>/',
        views.EditLocation.as_view(),
        name='location_edit'),
    # Locations list
    path(
        'locations/',
        views.LocationsList.as_view(),
        name='locations_list'),
    # Delete location
    path(
        'location/delete/<int:pk>/',
        views.location_delete,
        name='location_delete'),
    # Create new sub-location
    path(
        'sub-location/new/',
        views.CreateSubLocation.as_view(),
        name='sublocation_new'),
    # Edit existing sub-location
    path(
        'sub-location/edit/<int:pk>/',
        views.EditSubLocation.as_view(),
        name='sublocation_edit'),
    # Sub-locations list
    path(
        'sub-locations/',
        views.SubLocationsList.as_view(),
        name='sublocations_list'),
    # Delete sub-location
    path(
        'sub-location/delete/<int:pk>/',
        views.sublocation_delete,
        name='sublocation_delete'),
    # Create new item
    path(
        'item/new/',
        views.CreateItem.as_view(),
        name='item_new'),
    # Edit existing item
    path(
        'item/edit/<int:pk>/',
        views.EditItem.as_view(),
        name='item_edit'),
    # View existing item details
    path(
        'item/<int:pk>/',
        views.ItemDetails.as_view(),
        name='item_details'),
    # Items list
    path(
        'items/',
        views.ItemsList.as_view(),
        name='items_list'),
    # Delete item
    path(
        'item/delete/<int:pk>/',
        views.item_delete,
        name='item_delete'),
    # Create new move
    path(
        'move/new/<int:pk>/',
        views.CreateItemMove.as_view(),
        name='move_new'),
    # Item moves list
    path(
        'moves/<int:pk>/',
        views.ItemMovesList.as_view(),
        name='moves_list'),
    # Create new transfer
    path(
        'transfer/new/<int:pk>/',
        views.CreateItemTransfer.as_view(),
        name='transfer_new'),
]
