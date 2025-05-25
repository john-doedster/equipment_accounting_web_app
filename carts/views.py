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

    # Обновляем корзину и возвращаем JSON-ответ в любом случае
    user_cart = get_user_carts(request)
    cart_items_html = render_to_string(
        "carts/includes/included_cart.html", {"carts": user_cart}, request=request)

    response_data = {
        "message": "Продукт добавлен в корзину",
        "cart_items_html": cart_items_html,
    }
    return JsonResponse(response_data)
    

def cart_change(request):
    cart_id = request.POST.get("cart_id")
    quantity = request.POST.get("quantity")

    cart = Cart.objects.get(id=cart_id)

    cart.quantity = quantity
    cart.save()
    updated_quantity = cart.quantity

    user_cart = get_user_carts(request)

    cart_items_html = render_to_string(
        "carts/includes/included_cart.html", {"carts": user_cart}, request=request)

    response_data = {
        "message": "Количество изменено",
        "cart_items_html": cart_items_html,
        "quantity": updated_quantity,
    }
    return JsonResponse(response_data)


def cart_remove(request):
    
    cart_id = request.POST.get("cart_id")

    cart = Cart.objects.get(id=cart_id)
    quantity = cart.quantity
    cart.delete()

    user_cart = get_user_carts(request)


    cart_items_html = render_to_string(
        "carts/includes/included_cart.html", {"carts": user_cart}, request=request)

    response_data = {
        "message": "Товар удален",
        "cart_items_html": cart_items_html,
        "quantity_deleted": quantity,
    }

    return JsonResponse(response_data)

def download_cart_excel(request):
    # Получаем корзину текущего пользователя
    carts = Cart.objects.filter(user=request.user)
    
    # Создаем книгу Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Корзина"
    
    # Добавляем заголовки
    headers = ["ID", "Товар", "Количество", "Цена за шт.", "Скидка", "Итоговая цена"]
    ws.append(headers)
    
    # Добавляем данные
    for cart in carts:
        product = cart.product
        total_price = cart.quantity * product.sell_price()
        
        ws.append([
            product.id,
            product.name,
            cart.quantity,
            product.price,
            f"{product.discount}%" if product.discount else "Нет",
            total_price
        ])
    
    # Добавляем итоговую строку
    total_quantity = sum(cart.quantity for cart in carts)
    total_sum = sum(cart.quantity * cart.product.sell_price() for cart in carts)
    
    ws.append(["", "ИТОГО:", total_quantity, "", "", total_sum])
    
    # Настраиваем стили для итоговой строки
    for cell in ws[ws.max_row]:
        cell.font = cell.font.copy(bold=True)
    
    # Создаем HTTP ответ
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=cart.xlsx'
    wb.save(response)
    
    return response

