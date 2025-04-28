from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, get_object_or_404, render

from equipment.models import Products


def catalog(request, category_slug, page = 1):

    if category_slug == 'all':
        equipment = Products.objects.all()
    else:
        equipment = get_list_or_404(Products.objects.filter(category__slug=category_slug))
    
    paginator = Paginator(equipment, 2)
    current_page = paginator.page(page)

    context = {
        "title": "Home - Каталог",
        "equipment": current_page,
        "slug_url": category_slug
    }

    return render(request, "equipment/catalog.html", context)


def product(request,product_slug):

    product=Products.objects.get(slug=product_slug)

    context = {
        "product": product
    }

    return render(request, "equipment/product.html", context=context)
