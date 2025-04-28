from django.urls import path

from equipment import views

app_name = 'equipment'

urlpatterns = [
    path('<slug:category_slug>/', views.catalog, name='index'),
    path('<slug:category_slug>/<int:page>/', views.catalog, name='index'),
    path('product/<slug:product_slug>/', views.product, name='product'),
]
