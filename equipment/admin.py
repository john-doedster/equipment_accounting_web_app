from django.contrib import admin

#регистрируем модель таблицы в админке
from equipment.models import Categories, Products

#admin.site.register(Categories)
#admin.site.register(Products)

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name']

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'category', 'price', 'quantity', 'display_id']
    list_editable = ['price', 'quantity']
    search_fields = ['name', 'description']
    list_filter = ['category', 'quantity']
    fields = [
        'name',
        'category',
        'slug',
        'description',
        'image',
        ('price','discount'),
        'quantity'
    ]
