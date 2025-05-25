from datetime import datetime
from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from .models import Device, Category, ImportedDevice


class DeviceForm(forms.ModelForm):
    acceptance_date = forms.DateField(
        label=_("Дата принятия к учету"),  # Явно указываем метку
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        required=False
    )
    
    book_value = forms.DecimalField(
        label=_("Балансовая стоимость"),  # Явно указываем метку
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '1000',
            'class': 'form-control',
            'min': '0'
        }),
        required=False
    )
    
    quantity = forms.IntegerField(
        label=_("Количество"),  # Явно указываем метку
        widget=forms.NumberInput(attrs={
            'min': '1',
            'class': 'form-control'
        }),
        initial=1,
        required=False
    )

    class Meta:
        model = Device
        fields = [
            "name",
            "category",
            "inventory_number",
            "status",
            "location",
            "acceptance_date",
            "book_value",
            "quantity",
            "description",
        ]
        labels = {  # Добавляем блок с метками
            "name": _("Название устройства"),
            "category": _("Категория"),
            "inventory_number": _("Инвентарный номер"),
            "status": _("Статус"),
            "location": _("Местоположение"),
            "description": _("Описание"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "inventory_number": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "location": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": _("Подробное описание устройства"),
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].label = _("Категория")  # На всякий случай дублируем
        self.fields["category"].queryset = Category.objects.all().order_by("name")
        self.fields["category"].empty_label = "Выберите категорию"
        self.fields["category"].widget.attrs.update({"class": "form-select"})

    def clean_acceptance_date(self):
        date = self.cleaned_data.get('acceptance_date')
        if isinstance(date, str):
            try:
                return datetime.strptime(date, '%d.%m.%Y').date()
            except ValueError:
                try:
                    return datetime.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                    raise forms.ValidationError("Введите дату в формате ДД.ММ.ГГГГ")
        return date

    def clean_inventory_number(self):
        inventory_number = self.cleaned_data["inventory_number"]
        qs = Device.objects.filter(inventory_number=inventory_number)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                _("Устройство с таким инвентарным номером уже существует")
            )
        return inventory_number



class ExportForm(forms.Form):
    COLUMN_CHOICES = [
        ("name", "Название"),
        ("category", "Категория"),
        ("inventory_number", "Инв.номер"),
        ("status", "Статус"),
    ]
    columns = forms.MultipleChoiceField(
        choices=COLUMN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=["name", "category", "inventory_number"],
    )


class ImportExcelForm(forms.Form):
    file = forms.FileField(
        label="Excel файл",
        validators=[FileExtensionValidator(allowed_extensions=["xlsx", "xls"])],
    )

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(
                    "Файл слишком большой. Максимальный размер - 5MB"
                )
            if not file.name.endswith((".xlsx", ".xls")):
                raise forms.ValidationError("Неподдерживаемый формат файла")
        return file
    
class ImportedDeviceEditForm(forms.ModelForm):
    class Meta:
        model = ImportedDevice
        fields = ['row_number', 'asset_name', 'inventory_number', 
                 'acceptance_date', 'book_value', 'quantity']
        
        widgets = {
            'acceptance_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'book_value': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': '1', 'class': 'form-control'}),
        }
