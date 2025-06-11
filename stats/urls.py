# stats/urls.py
from django.urls import path
from .views import equipment_statistics

app_name = 'stats'  # Пространство имён приложения

urlpatterns = [
    path('', equipment_statistics, name='equipment_stats'),
]