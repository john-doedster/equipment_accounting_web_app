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
]