from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from openpyxl import Workbook

from carts.models import Cart
from carts.utils import get_user_carts
from equipment.models import Products

def cart_add(request):
    product_id = request.POST.get("product_id")
    product = Products.objects.get(id=product_id)
    
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, product=product)
        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(user=request.user, product=product, quantity=1)
    else:
        carts = Cart.objects.filter(session_key=request.session.session_key, product=product)
        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(session_key=request.session.session_key, product=product, quantity=1)

    user_cart = get_user_carts(request)
    
    # Определяем какой шаблон использовать
    if request.GET.get('modal') == 'true':
        template = "carts/includes/included_cart_modal.html"
    else:
        template = "carts/includes/included_cart.html"
    
    cart_items_html = render_to_string(
        template, {
            "carts": user_cart,
            "title": "Список оборудования"
        }, request=request)

    response_data = {
        "message": "Оборудование добавлено в список",
        "cart_items_html": cart_items_html,
        "cart_total_quantity": user_cart.total_quantity()
    }
    return JsonResponse(response_data)

def cart_change(request):
    cart_id = request.POST.get("cart_id")
    quantity = request.POST.get("quantity")

    cart = Cart.objects.get(id=cart_id)
    cart.quantity = quantity
    cart.save()

    user_cart = get_user_carts(request)
    
    # Определяем какой шаблон использовать
    if request.GET.get('modal') == 'true':
        template = "carts/includes/included_cart_modal.html"
    else:
        template = "carts/includes/included_cart.html"
    
    cart_items_html = render_to_string(
        template, {
            "carts": user_cart,
            "title": "Список оборудования"
        }, request=request)

    response_data = {
        "message": "Количество изменено",
        "cart_items_html": cart_items_html,
        "quantity": cart.quantity,
        "cart_total_quantity": user_cart.total_quantity()
    }
    return JsonResponse(response_data)

def cart_remove(request):
    cart_id = request.POST.get("cart_id")
    cart = Cart.objects.get(id=cart_id)
    quantity = cart.quantity
    cart.delete()

    user_cart = get_user_carts(request)
    
    # Генерируем HTML для обоих случаев (обычный и модальный)
    cart_items_html = render_to_string(
        "carts/includes/included_cart.html", {
            "carts": user_cart,
            "title": "Список оборудования"
        }, request=request)
    
    modal_html = render_to_string(
        "carts/includes/included_cart_modal.html", {
            "carts": user_cart,
            "title": "Список оборудования"
        }, request=request)

    response_data = {
        "message": "Оборудование удалено из списка",
        "cart_items_html": cart_items_html,
        "modal_html": modal_html,
        "quantity_deleted": quantity,
        "cart_total_quantity": user_cart.total_quantity()
    }
    return JsonResponse(response_data)

def download_cart_excel(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        position = request.POST.get('position', '')
        conditions = request.POST.getlist('conditions[]')
        carts = Cart.objects.filter(user=request.user)
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Список оборудования"
        
        # Заголовки
        ws.append(["ФИО ответственного:", full_name])
        ws.append(["Должность:", position])
        ws.append([])
        ws.append(["ID", "Название", "Количество", "Состояние"])
        
        # Данные
        for i, cart in enumerate(carts):
            ws.append([
                cart.product.id,
                cart.product.name,
                cart.quantity,
                conditions[i] if i < len(conditions) else "Не указано"
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=equipment_list.xlsx'
        wb.save(response)
        return response
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

