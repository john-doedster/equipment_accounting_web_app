from django.shortcuts import redirect
from django.contrib import messages
from carts.models import Cart
from .models import Order, OrderItem

def create_order(request):
    if request.method == 'POST':
        # Получаем корзину пользователя
        carts = Cart.objects.filter(user=request.user)
        
        if not carts.exists():
            messages.error(request, "Ваша корзина пуста")
            return redirect('users:profile')
        
        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            requires_delivery=False,
            payment_on_get=True,
            status='Принято'
        )
        
        # Добавляем товары в заказ
        for cart in carts:
            OrderItem.objects.create(
                order=order,
                product=cart.product,
                quantity=cart.quantity,
                condition=request.POST.get(f'condition_{cart.id}', 'Не указано')
            )
        
        # Очищаем корзину
        carts.delete()
        
        messages.success(request, "Оборудование успешно записано на вас")
        return redirect('users:profile')
    
    return redirect('carts:cart')