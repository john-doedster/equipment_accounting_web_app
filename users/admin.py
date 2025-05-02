from django.contrib import admin

#регистрируем модель таблицы в админке
from users.models import User

admin.site.register(User)
