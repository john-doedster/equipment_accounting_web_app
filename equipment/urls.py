from django.urls import path

from equipment import views

app_name = 'equipment'

urlpatterns = [
    path('', views.catalog, name='index'),
    path('product/<slug:product_slug>/', views.product, name='product'),
]
