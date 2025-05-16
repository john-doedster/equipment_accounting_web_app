from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from .models import Device, Category


class DeviceForm(forms.ModelForm):

    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by("name"),
        label=_("Категория"),
        required=False,  # Если категория не обязательна
        empty_label="Выберите категорию",  # Заменяем прочерк на это текст
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Device
        fields = [
            "name",
            "category",
            "inventory_number",
            "status",
            "location",
            "description",
        ]
        labels = {
            "name": _("Название устройства"),
            "category": _("Категория"),
            "inventory_number": _("Инвентарный номер"),
            "status": _("Статус"),
            "location": _("Местоположение"),
            "description": _("Описание"),
        }
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": _("Подробное описание устройства"),
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
        help_texts = {
            "inventory_number": _("Уникальный идентификатор устройства"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].empty_label = "Выберите категорию"
        self.fields["category"].queryset = Category.objects.all().order_by("name")
        self.fields["category"].widget.attrs.update({"class": "form-select"})

        # Добавляем классы form-control для всех полей
        for field_name, field in self.fields.items():
            if field_name not in ["status", "category"]:
                field.widget.attrs["class"] = "form-control"

        # Оптимизируем queryset для категорий
        self.fields["category"].queryset = Category.objects.all().order_by("name")

    def clean_inventory_number(self):
        inventory_number = self.cleaned_data["inventory_number"]
        # Проверка на уникальность (исключая текущий объект при редактировании)
        qs = Device.objects.filter(inventory_number=inventory_number)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                _("Устройство с таким инвентарным номером уже существует")
            )
        return inventory_number

    # forms.py


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
