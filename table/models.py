import uuid
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название категории"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")


class Device(models.Model):
    class Status(models.TextChoices):
        IN_STOCK = 'IN', _('На складе')
        IN_USE = 'USE', _('В использовании')
        UNDER_REPAIR = 'REP', _('В ремонте')
        WRITTEN_OFF = 'OFF', _('Списано')

    name = models.CharField(max_length=100, verbose_name=_("Название устройства"))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Категория")
    )
    inventory_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Инвентарный номер")
    )
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.IN_STOCK,
        verbose_name=_("Статус")
    )
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Местоположение"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"

    def get_absolute_url(self):
        return reverse('table:device_detail', args=[str(self.id)])

    class Meta:
        verbose_name = _("Устройство")
        verbose_name_plural = _("Устройства")
        ordering = ['-created_at']

class ImportedDevice(models.Model):
    row_number = models.CharField(max_length=50, verbose_name="№ п/п")
    asset_name = models.CharField(max_length=255, verbose_name="Основное средство")
    inventory_number = models.CharField(max_length=100, verbose_name="Инвентарный номер")
    acceptance_date = models.DateField(verbose_name="Дата принятия к учету")
    book_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Балансовая стоимость")
    quantity = models.IntegerField(verbose_name="Количество")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.asset_name} ({self.inventory_number})"

class SavedTable(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название таблицы")
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    devices = models.ManyToManyField(ImportedDevice)
    slug = models.SlugField(max_length=200, unique=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)   