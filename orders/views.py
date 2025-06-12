from django.shortcuts import redirect
from django.contrib import messages
from carts.models import Cart
from .models import Order, OrderItem

def create_order(request):
    if request.method == 'POST':
        carts = Cart.objects.filter(user=request.user)
        
        if not carts.exists():
            messages.error(request, "Ваша корзина пуста")
            return redirect('users:profile')
        
        # Проверка наличия товаров
        for cart in carts:
            if cart.product.quantity < cart.quantity:
                messages.error(request, f"Недостаточно товара '{cart.product.name}' на складе")
                return redirect('carts:cart')
        
        # Создание заказа
        order = Order.objects.create(
            user=request.user,
            requires_delivery=False,
            payment_on_get=True,
            status='Закреплено',  # Изменили статус для точной статистики
            office=request.POST.get('office')
        )
        
        # Создание позиций заказа (БЕЗ уменьшения quantity!)
        for cart in carts:
            OrderItem.objects.create(
                order=order,
                product=cart.product,
                name=cart.product.name,
                quantity=cart.quantity,
                condition=request.POST.get(f'condition_{cart.id}', 'Не указано')
            )
        
        # Очистка корзины
        carts.delete()
        
        messages.success(request, "Оборудование успешно записано на вас")
        return redirect('users:profile')
    
    return redirect('carts:cart')