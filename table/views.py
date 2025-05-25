from datetime import datetime
import json
import numbers
from tkinter.font import Font
import uuid
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.template.defaultfilters import slugify
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
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext_lazy as _
from openpyxl import Workbook
from .models import Device, Category, SavedTable
from .forms import DeviceForm, ImportedDeviceEditForm
import csv
from io import StringIO
import pandas as pd
from .forms import ImportExcelForm
from .models import ImportedDevice
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


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
        context["title"] = _("Список устройств")
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

    def get_initial(self):
        initial = super().get_initial()
        if self.object.acceptance_date:
            initial['acceptance_date'] = self.object.acceptance_date.strftime('%Y-%m-%d')
        return initial

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Удаление устройства")
        return context

class DeviceDetailView(DetailView):
    model = Device
    template_name = "table/device_detail.html"
    context_object_name = "device"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Просмотр устройства")
        return context 


def export_devices_to_excel(request):
    # Создаем книгу
    wb = Workbook()
    ws = wb.active
    ws.title = "Устройства"

    # Заголовки как в таблице на главной странице
    headers = [
        "№ п/п",
        "Название",
        "Категория",
        "Инвентарный номер",
        "Расположение",
        "Дата принятия к учету",
        "Балансовая стоимость",
        "Количество",
        "Статус"
    ]
    ws.append(headers)

    # Данные
    devices = Device.objects.select_related("category").all()
    for index, device in enumerate(devices, start=1):
        ws.append([
            index,  # № п/п
            device.name or "-",
            device.category.name if device.category else "-",
            device.inventory_number or "-",
            device.get_location_display() or "-",
            device.acceptance_date.strftime("%d.%m.%Y") if device.acceptance_date else "-",
            device.book_value or "-",
            device.quantity or "1",
            device.get_status_display() or "-"
        ])

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


@transaction.atomic
@login_required
def import_devices(request):
    if request.method == 'POST':
        try:
            # Валидация файла
            if not request.FILES.get('file'):
                raise ValueError("Файл не был выбран")
            
            file = request.FILES['file']
            if not file.name.endswith(('.xlsx', '.xls')):
                raise ValueError("Поддерживаются только файлы Excel (.xlsx, .xls)")
            
            # Чтение и обработка данных
            df = pd.read_excel(file, engine='openpyxl')
            required_columns = ['№ п/п', 'Основное средство', 'Инвентарный номер', 
                              'Дата принятия к учету', 'Балансовая стоимость', 'Количество']
            
            if missing := [col for col in required_columns if col not in df.columns]:
                raise ValueError(f"Отсутствуют обязательные столбцы: {', '.join(missing)}")
            
            devices = []
            for index, row in df.iterrows():
                try:
                    # Обработка и валидация данных
                    acceptance_date = (datetime.strptime(row['Дата принятия к учету'], '%d.%m.%Y').date() 
                                      if isinstance(row['Дата принятия к учету'], str) 
                                      else row['Дата принятия к учету'] or datetime.now().date())
                    
                    if pd.isna(row['Основное средство']) or pd.isna(row['Инвентарный номер']):
                        raise ValueError(f"Строка {index+2}: отсутствует название или инвентарный номер")
                    
                    devices.append(ImportedDevice(
                        row_number=str(row['№ п/п']),
                        asset_name=str(row['Основное средство']),
                        inventory_number=str(row['Инвентарный номер']),
                        acceptance_date=acceptance_date,
                        book_value=float(row['Балансовая стоимость']),
                        quantity=int(row['Количество'])
                    ))
                except Exception as e:
                    raise ValueError(f"Строка {index+2}: {str(e)}") from e
            
            # Проверка дубликатов
            if len(inv_nums := [d.inventory_number for d in devices]) != len(set(inv_nums)):
                duplicates = {n for n in inv_nums if inv_nums.count(n) > 1}
                raise ValueError(f"Дубликаты инвентарных номеров: {', '.join(duplicates)}")
            
            # Сохранение
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
            error_msg = str(e)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('table:import_devices')
    
    # GET запрос
    form = ImportExcelForm()
    return render(request, 'table/import.html', {
        'form': form,
        'title': _("Импорт устройств"),
    })


def imported_devices_list(request):
    device_list = ImportedDevice.objects.all().order_by('-created_at')
    paginator = Paginator(device_list, 15)  # 15 элементов на странице
    page_number = request.GET.get('page')
    devices = paginator.get_page(page_number)
    
    context = {
        'devices': devices,
        'title': _("Импортированные устройства"),
    }
    return render(request, 'table/imported_list.html', context)



@login_required
def imported_device_detail(request, pk):
    device = get_object_or_404(ImportedDevice, pk=pk)
    table_slug = request.GET.get('table_slug')

    return render(request, 'table/imported_device_detail.html', {
        'device': device,
        'table_slug': table_slug,  # Передаем в шаблон
        'title': _("Просмотр устройства"),
    })

@login_required
def imported_device_edit(request, pk):
    device = get_object_or_404(ImportedDevice, pk=pk)
    table_slug = request.GET.get('table_slug')
    
    if request.method == 'POST':
        form = ImportedDeviceEditForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, _("Устройство успешно обновлено"))
            if table_slug:
                return redirect('table:view_saved_table', slug=table_slug)
            return redirect('table:imported_devices_list')
    else:
        form = ImportedDeviceEditForm(instance=device)
    
    return render(request, 'table/imported_device_edit.html', {
        'form': form,
        'device': device,
        'table_slug': table_slug,
        'title': _("Редактирование устройства"),
    })

@login_required
@require_POST
def imported_device_delete(request, pk):
    device = get_object_or_404(ImportedDevice, pk=pk)
    table_slug = request.POST.get('table_slug')
    device.delete()
    messages.success(request, _("Устройство успешно удалено"))
    
    if table_slug:
        return redirect('table:view_saved_table', slug=table_slug)
    return redirect('table:imported_devices_list')

#Скачивание отредактированных данных из загруженной таблицы Excel

def export_edited_devices(request):
    # Создаем книгу Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Edited Devices"

    # Заголовки
    headers = ['№ п/п', 'Основное средство', 'Инвентарный номер', 
               'Дата принятия', 'Балансовая стоимость', 'Количество']
    ws.append(headers)

    # Данные
    devices = ImportedDevice.objects.all().order_by('-created_at')
    for device in devices:
        ws.append([
            device.row_number,
            device.asset_name,
            device.inventory_number,
            device.acceptance_date.strftime('%d.%m.%Y'),
            device.book_value,
            device.quantity
        ])

    # Настройка ответа
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=edited.xlsx'
    wb.save(response)
    
    return response

@login_required
def save_current_table(request):
    if request.method == 'POST':
        title = request.POST.get('table_title', 'Сохраненная таблица')
        
        # Создаем сохраненную таблицу
        saved_table = SavedTable.objects.create(
            title=title,
            creator=request.user,
            slug=slugify(title) + '-' + str(uuid.uuid4())[:8]
        )
        
        # Добавляем текущие устройства
        devices = ImportedDevice.objects.all()
        saved_table.devices.set(devices)
        
        messages.success(request, f"Таблица '{title}' успешно сохранена")
        return redirect('table:view_saved_table', slug=saved_table.slug)

@login_required
def view_saved_table(request, slug):
    saved_table = get_object_or_404(SavedTable, slug=slug)
    devices = saved_table.devices.all()
    
    return render(request, 'table/saved_table.html', {
        'saved_table': saved_table,
        'devices': devices,
        'title': saved_table.title
    })

def list_saved_tables(request):
    tables = SavedTable.objects.filter(creator=request.user)\
                             .annotate(device_count=Count('devices'))\
                             .order_by('-created_at')
    return render(request, 'table/saved_tables_list.html', {
        'tables': tables,
        'title': 'Сохраненные таблицы'
    })


@login_required
def edit_saved_table(request, slug):
    saved_table = get_object_or_404(SavedTable, slug=slug, creator=request.user)
    
    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            saved_table.title = new_title
            saved_table.save()
            messages.success(request, 'Название таблицы обновлено')
            return redirect('table:saved_tables_list')  # Убрал slug из redirect
        else:
            messages.error(request, 'Название не может быть пустым')
    
    return render(request, 'table/edit_saved_table.html', {
        'saved_table': saved_table,
        'title': f'Редактирование: {saved_table.title}'
    })

@login_required
@require_POST
def delete_saved_table(request, slug):
    saved_table = get_object_or_404(SavedTable, slug=slug, creator=request.user)
    title = saved_table.title
    saved_table.delete()
    messages.success(request, f'Таблица "{title}" успешно удалена')
    return redirect('table:saved_tables_list')

def export_saved_table(request, slug):
    try:
        saved_table = get_object_or_404(SavedTable, slug=slug)
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Устройства"
        
        headers = ['№ п/п', 'Основное средство', 'Инвентарный номер', 
                  'Дата принятия к учету', 'Балансовая стоимость', 'Количество']
        ws.append(headers)
        
        for idx, device in enumerate(saved_table.devices.all(), start=1):
            ws.append([
                idx,
                getattr(device, 'asset_name', ''),
                getattr(device, 'inventory_number', ''),
                device.acceptance_date.strftime('%d.%m.%Y') if getattr(device, 'acceptance_date', None) else '',
                getattr(device, 'book_value', ''),
                getattr(device, 'quantity', '')
            ])
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{saved_table.title}.xlsx"'
        wb.save(response)
        return response
        
    except Exception as e:
        return HttpResponse(f"Произошла ошибка: {str(e)}", status=500)


def delete_all_imported_devices(request):
    if request.method == 'POST':
        # Получаем количество удаляемых устройств (для сообщения)
        count = ImportedDevice.objects.count()
        
        # Удаляем все устройства
        ImportedDevice.objects.all().delete()
        
        # Добавляем сообщение об успешном удалении
        messages.success(request, f'Успешно удалено {count} устройств.')
        
        # Перенаправляем на страницу с импортированными устройствами
        return redirect('table:import_devices')  # Замените на ваш URL name
    
    # Если запрос не POST, перенаправляем на главную
    return redirect('table:device_list')  # Замените на ваш основной URL