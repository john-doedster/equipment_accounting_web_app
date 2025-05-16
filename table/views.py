from datetime import datetime
import numbers
from tkinter.font import Font
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from openpyxl import Workbook
from .models import Device, Category
from .forms import DeviceForm
import csv
from io import StringIO
import pandas as pd
from .forms import ImportExcelForm
from .models import ImportedDevice


class DeviceListView(ListView):
    model = Device
    template_name = "table/device_list.html"
    context_object_name = "devices"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по статусу (если передан параметр status)
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        # Фильтрация по категории (если передан параметр category)
        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["status_choices"] = Device.Status.choices
        return context


class DeviceCreateView(SuccessMessageMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = "table/device_form.html"
    success_url = reverse_lazy("table:device_list")
    success_message = _("Устройство успешно создано")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class DeviceUpdateView(SuccessMessageMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = "table/device_form.html"
    success_url = reverse_lazy("table:device_list")
    success_message = _("Устройство успешно обновлено")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class DeviceDeleteView(DeleteView):
    model = Device
    template_name = "table/device_confirm_delete.html"
    success_url = reverse_lazy("table:device_list")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _("Устройство успешно удалено"))
        return response


class DeviceDetailView(DetailView):
    model = Device
    template_name = "table/device_detail.html"
    context_object_name = "device"


def export_devices_to_excel(request):
    # Создаем книгу
    wb = Workbook()
    ws = wb.active
    ws.title = "Устройства"

    # Простые заголовки без стилей
    ws.append(["ID", "Название", "Категория", "Инв.номер"])

    # Данные
    devices = Device.objects.select_related("category")
    for device in devices:
        ws.append(
            [
                device.id,
                device.name,
                device.category.name if device.category else "",
                device.inventory_number,
            ]
        )

    # Настройка ответа
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=devices.xlsx"
    wb.save(response)

    return response


def export_devices(request, format="xlsx"):
    devices = Device.objects.all().select_related("category")

    if format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Название", "Категория", "Инв.номер", "Статус"])

        for device in devices:
            writer.writerow(
                [
                    device.id,
                    device.name,
                    device.category.name if device.category else "",
                    device.inventory_number,
                    device.get_status_display(),
                ]
            )

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=devices.csv"
        return response

    else:  # XLSX
        wb = Workbook()
        ws = wb.active
        # ... остальной код экспорта в Excel ...
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=devices.xlsx"
        wb.save(response)
        return response


def import_devices(request):
    if request.method == 'POST':
        # Проверка наличия файла
        if not request.FILES.get('file'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Файл не был выбран'
                }, status=400)
            messages.error(request, "Файл не был выбран")
            return redirect('table:import_devices')
        
        file = request.FILES['file']
        
        # Проверка расширения файла
        if not file.name.endswith(('.xlsx', '.xls')):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Поддерживаются только файлы Excel (.xlsx, .xls)'
                }, status=400)
            messages.error(request, "Поддерживаются только файлы Excel (.xlsx, .xls)")
            return redirect('table:import_devices')
        
        try:
            # Чтение Excel файла
            df = pd.read_excel(file)
            
            # Проверка обязательных столбцов
            required_columns = [
                '№ п/п',
                'Основное средство', 
                'Инвентарный номер',
                'Дата принятия к учету',
                'Балансовая стоимость',
                'Количество'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Отсутствуют обязательные столбцы: {', '.join(missing_columns)}"
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': error_msg
                    }, status=400)
                messages.error(request, error_msg)
                return redirect('table:import_devices')
            
            # Подготовка данных для импорта
            devices = []
            for index, row in df.iterrows():
                try:
                    # Обработка даты
                    acceptance_date = row['Дата принятия к учету']
                    if pd.isna(acceptance_date):
                        acceptance_date = datetime.now().date()
                    elif isinstance(acceptance_date, str):
                        acceptance_date = datetime.strptime(acceptance_date, '%Y-%m-%d').date()
                    
                    # Проверка обязательных полей
                    if pd.isna(row['Основное средство']) or pd.isna(row['Инвентарный номер']):
                        raise ValueError(f"Строка {index+2}: отсутствует название или инвентарный номер")
                    
                    devices.append(
                        ImportedDevice(
                            row_number=str(row['№ п/п']),
                            asset_name=str(row['Основное средство']),
                            inventory_number=str(row['Инвентарный номер']),
                            acceptance_date=acceptance_date,
                            book_value=float(row['Балансовая стоимость']),
                            quantity=int(row['Количество'])
                        )
                    )
                except Exception as e:
                    error_msg = f"Ошибка в строке {index+2}: {str(e)}"
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': error_msg
                        }, status=400)
                    messages.error(request, error_msg)
                    return redirect('table:import_devices')
            
            # Проверка на дубликаты инвентарных номеров
            inventory_numbers = [d.inventory_number for d in devices]
            if len(inventory_numbers) != len(set(inventory_numbers)):
                duplicates = {num for num in inventory_numbers if inventory_numbers.count(num) > 1}
                error_msg = f"Обнаружены дубликаты инвентарных номеров: {', '.join(duplicates)}"
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': error_msg
                    }, status=400)
                messages.error(request, error_msg)
                return redirect('table:import_devices')
            
            # Сохранение в транзакции
            with transaction.atomic():
                ImportedDevice.objects.bulk_create(devices)
            
            success_msg = f"Успешно импортировано {len(devices)} устройств"
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': success_msg,
                    'redirect_url': reverse('table:imported_devices_list')
                })
            
            messages.success(request, success_msg)
            return redirect('table:imported_devices_list')
            
        except Exception as e:
            error_msg = f"Ошибка при обработке файла: {str(e)}"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': error_msg
                }, status=400)
            messages.error(request, error_msg)
    
    # GET запрос или ошибка валидации
    form = ImportExcelForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': 'Неверный метод запроса'
        }, status=400)
    
    return render(request, 'table/import.html', {'form': form})

def imported_devices_list(request):
    """Отображение списка импортированных устройств"""
    devices = ImportedDevice.objects.all().order_by('-created_at')
    return render(request, 'table/imported_list.html', {'devices': devices})