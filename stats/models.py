from django.db import models

from django.db import models
from equipment.models import Products, Categories

class EquipmentStats(models.Model):
    date = models.DateField(auto_now_add=True)
    total_equipment = models.IntegerField()
    assigned_count = models.IntegerField()
    available_count = models.IntegerField()
    popular_categories = models.JSONField()
    
    class Meta:
        ordering = ['-date']