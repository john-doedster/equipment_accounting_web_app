from django.urls import path

from equipment import views

app_name = 'equipment'

urlpatterns = [
    path('<slug:category_slug>/', views.catalog, name='index'),
    path('search/', views.catalog, name='search'),
    path('product/<slug:product_slug>/', views.product, name='product'),
]
