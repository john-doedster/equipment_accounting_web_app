from django.urls import path
from . import views
from .views import export_devices_to_excel
from .views import import_devices, imported_devices_list

app_name = 'table'

urlpatterns = [
    path('', views.DeviceListView.as_view(), name='device_list'),
    path('create/', views.DeviceCreateView.as_view(), name='device_create'),
    path('<int:pk>/', views.DeviceDetailView.as_view(), name='device_detail'),
    path('<int:pk>/update/', views.DeviceUpdateView.as_view(), name='device_update'),
    path('<int:pk>/delete/', views.DeviceDeleteView.as_view(), name='device_delete'),
    path('export/', export_devices_to_excel, name='device_export'),
    path('import/', views.import_devices, name='import_devices'),
    path('imported-devices/', views.imported_devices_list, name='imported_devices_list'),


    path('imported-devices/<int:pk>/', views.imported_device_detail, name='imported_device_detail'),
    path('imported-devices/<int:pk>/edit/', views.imported_device_edit, name='imported_device_edit'),
    path('imported-devices/<int:pk>/delete/', views.imported_device_delete, name='imported_device_delete'),

    path('export-edited-devices/', views.export_edited_devices, name='export_edited_devices'),

    path('save-table/', views.save_current_table, name='save_table'),
    path('saved-tables/', views.list_saved_tables, name='saved_tables_list'),
    path('saved-table/<slug:slug>/', views.view_saved_table, name='view_saved_table'),

    path('saved-table/<slug:slug>/edit/', views.edit_saved_table, name='edit_saved_table'),

    path('saved-table/<slug:slug>/delete/', views.delete_saved_table, name='delete_saved_table'),
]