# admin.py
from django.contrib import admin
from .models import Device
from django.http import HttpResponse
import csv

@admin.action(description='Экспорт выбранных в CSV')
def export_selected(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['ID', 'Название', 'Категория'])
    
    for device in queryset:
        writer.writerow([device.id, device.name, device.category.name])
    
    response['Content-Disposition'] = 'attachment; filename=selected_devices.csv'
    return response

class DeviceAdmin(admin.ModelAdmin):
    actions = [export_selected]

admin.site.register(Device, DeviceAdmin)
