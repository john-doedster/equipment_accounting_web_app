from django.shortcuts import get_object_or_404, render

from equipment.models import Products


def catalog(request, category_slug):

    if category_slug == 'all':
        equipment = Products.objects.all()
    else:
        equipment = get_object_or_404(Products.objects.filter(category__slug=category_slug))
    
    context = {
        "title": "Home - Каталог",
        "equipment": equipment,
    }

    return render(request, "equipment/catalog.html", context)


def product(request,product_slug):

    product=Products.objects.get(slug=product_slug)

    context = {
        "product": product
    }

    return render(request, "equipment/product.html", context=context)
