import numbers
from tkinter.font import Font
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from openpyxl import Workbook
from .models import Device, Category
from .forms import DeviceForm 
import csv
from io import StringIO

class DeviceListView(ListView):
    model = Device
    template_name = 'table/device_list.html'
    context_object_name = 'devices'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по статусу (если передан параметр status)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        # Фильтрация по категории (если передан параметр category)
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['status_choices'] = Device.Status.choices
        return context


class DeviceCreateView(SuccessMessageMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = 'table/device_form.html'
    success_url = reverse_lazy('table:device_list')
    success_message = _("Устройство успешно создано")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class DeviceUpdateView(SuccessMessageMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = 'table/device_form.html'
    success_url = reverse_lazy('table:device_list')
    success_message = _("Устройство успешно обновлено")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class DeviceDeleteView(DeleteView):
    model = Device
    template_name = 'table/device_confirm_delete.html'
    success_url = reverse_lazy('table:device_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _("Устройство успешно удалено"))
        return response


class DeviceDetailView(DetailView):
    model = Device
    template_name = 'table/device_detail.html'
    context_object_name = 'device'




def export_devices_to_excel(request):
    # Создаем книгу
    wb = Workbook()
    ws = wb.active
    ws.title = "Устройства"
    
    # Простые заголовки без стилей
    ws.append(['ID', 'Название', 'Категория', 'Инв.номер'])
    
    # Данные
    devices = Device.objects.select_related('category')
    for device in devices:
        ws.append([
            device.id,
            device.name,
            device.category.name if device.category else "",
            device.inventory_number
        ])
    
    # Настройка ответа
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=devices.xlsx'
    wb.save(response)
    
    return response

def export_devices(request, format='xlsx'):
    devices = Device.objects.all().select_related('category')
    
    if format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Название', 'Категория', 'Инв.номер', 'Статус'])
        
        for device in devices:
            writer.writerow([
                device.id,
                device.name,
                device.category.name if device.category else "",
                device.inventory_number,
                device.get_status_display()
            ])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=devices.csv'
        return response
    
    else:  # XLSX
        wb = Workbook()
        ws = wb.active
        # ... остальной код экспорта в Excel ...
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=devices.xlsx'
        wb.save(response)
        return response