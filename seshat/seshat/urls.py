"""
SESHAT URL configuration

https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.urls import path, include

from . import views

urlpatterns = [
    # multi language application
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # Index page (dashboard)
    path('', views.index, name='Index'),
    # backup page
    path('backup/', views.backup, name='Backup'),
    # download backup file
    path(
        'backup/download/<str:file_name>/',
        views.backup_download,
        name='DownloadBackup'),
    # restore page
    path('restore/', views.restore, name='Restore'),
    # export page
    path('export/', views.export_data, name='Export'),
    # import page
    path('import/', views.import_data, name='Import'),
    # download import template file
    path(
        'import/template/<str:module>/',
        views.import_template,
        name='ImportTemplate'),
    # account application for user accounts and administration
    path('admin/', include('account.urls')),
    # stock application for items, categories and locations
    path('stock/', include('stock.urls')),
    # customer application for customers and their companies
    path('customers/', include('customer.urls')),
    # vendor application for vendors and their companies
    path('vendors/', include('vendor.urls')),
    # purchase application for purchase orders
    path('purchases/', include('purchase.urls')),
    # sale application for sale orders
    path('sales/', include('sale.urls')),
    # remove prefix for the default language
    prefix_default_language=False,
)

# media and static files while developing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# error handlers
handler400 = views.error_400
handler403 = views.error_403
handler404 = views.error_404
handler500 = views.error_500
