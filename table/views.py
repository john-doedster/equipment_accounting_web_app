from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Device, Category
from .forms import DeviceForm  # Создадим этот файл следующим шагом

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