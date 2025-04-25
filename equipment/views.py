from django.shortcuts import render

from equipment.models import Products


def catalog(request):

    equipment = Products.objects.all()

    context = {
        "title": "Home - Каталог",
        "equipment": equipment,
    }

    return render(request, "equipment/catalog.html", context)


def product(request):
    return render(request, "equipment/product.html")
