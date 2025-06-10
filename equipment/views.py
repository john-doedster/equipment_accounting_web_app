from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, get_object_or_404, render
import qrcode
import base64
from io import BytesIO
import json

from equipment.models import Products
from equipment.utils import q_search


def catalog(request, category_slug=None):
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)

    if category_slug == 'all':
        equipment = Products.objects.all()
    elif query:
        equipment = q_search(query)
    else:
        equipment = get_list_or_404(Products.objects.filter(category__slug=category_slug))
    
    if order_by and order_by != "default":
        equipment = equipment.order_by(order_by)

    paginator = Paginator(equipment, 3)
    current_page = paginator.page(int(page))

    context = {
        "title": "Каталог",
        "equipment": current_page,
        "slug_url": category_slug
    }

    return render(request, "equipment/catalog.html", context)


def product(request, product_slug):
    product = Products.objects.get(slug=product_slug)
    
    # Формируем данные для QR-кода
    product_data = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "category": product.category.name,
        "slug": product.slug,
        "image_url": product.image.url if product.image else None
    }
    
    # Генерируем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(product_data, ensure_ascii=False))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    context = {
        "product": product,
        "title": "Подробнее об устройстве",
        "slug_url": product.category.slug,
        "qr_code": f"data:image/png;base64,{qr_code}"
    }

    return render(request, "equipment/product.html", context=context)