from django.shortcuts import render

def catalog(request):
    return render(request, 'equipment/catalog.html')

def product(request):
    return render(request, 'equipment/product.html')
