from django.shortcuts import render

from equipment.models import Products


def catalog(request):

    equipment = Products.objects.all()

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
