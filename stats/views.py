from django.shortcuts import render
from django.db.models import Count, Sum, Q, F  
from equipment.models import Products, Categories
from orders.models import OrderItem, Order
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def equipment_statistics(request):
    # Основные показатели с защитой от отрицательных значений
    total_products = Products.objects.count()
    total_quantity = Products.objects.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Статистика по закрепленному оборудованию с проверкой
    assigned_stats = OrderItem.objects.aggregate(
        items_count=Count('id', distinct=True),
        quantity_sum=Sum('quantity')
    )
    assigned_items = assigned_stats['items_count'] or 0
    assigned_quantity = assigned_stats['quantity_sum'] or 0
    
     # Рассчитываем доступное оборудование правильно
    # Для доступных позиций - считаем продукты, у которых quantity > assigned_qty
    available_products = Products.objects.annotate(
        assigned_qty=Sum('orderitem__quantity', default=0)
    ).filter(
        quantity__gt=F('assigned_qty')
    ).count()
    
    # Для доступного количества - разница общего и закрепленного
    available_quantity = max(total_quantity - assigned_quantity, 0)

    # Проверка на превышение закрепленного количества
    if assigned_quantity > total_quantity:
        logger.warning(
            f"Закрепленное количество ({assigned_quantity}) превышает общее ({total_quantity})"
        )
    
    # Статистика по категориям с защитой от None
    categories_stats = (
        Products.objects
        .values('category__name')
        .annotate(
            total=Count('id'),
            total_qty=Sum('quantity'),
            assigned=Count('orderitem'),
            assigned_qty=Sum('orderitem__quantity', default=0)  # Защита от None
        )
        .order_by('-total_qty')
    )
    
    # Топ товаров с проверкой количества
    popular_products = (
        Products.objects
        .annotate(
            assigned_count=Count('orderitem'),
            assigned_qty=Sum('orderitem__quantity', default=0)
        )
        .filter(quantity__gt=0)  # Исключаем нулевые количества
        .order_by('-quantity')[:10]
    )
    
    # Остальной код остается без изменений
    rooms_stats = (
        Order.objects
        .exclude(office__isnull=True)
        .exclude(office='')
        .values('office')
        .annotate(
            equipment_count=Count('orderitem'),
            total_quantity=Sum('orderitem__quantity', default=0)
        )
        .order_by('-equipment_count')[:10]
    )
    
    date_stats = []
    for i in range(30, -1, -1):
        date = (datetime.now() - timedelta(days=i)).date()
        assigned = Order.objects.filter(
            created_timestamp__date=date
        ).aggregate(
            count=Count('id'),
            qty=Sum('orderitem__quantity', default=0)
        )
        
        returned = Order.objects.filter(
            orderitem__created_timestamp__date=date,
            status__icontains='возврат'
        ).aggregate(
            count=Count('id'),
            qty=Sum('orderitem__quantity', default=0)
        )
        
        date_stats.append({
            'date': date.strftime('%d.%m'),
            'assigned_count': assigned['count'] or 0,
            'assigned_qty': assigned['qty'] or 0,
            'returned_count': returned['count'] or 0,
            'returned_qty': returned['qty'] or 0,
        })
    
    context = {
        'title': 'Статистика',
        'total_products': total_products,
        'total_quantity': total_quantity,
        'assigned_items': assigned_items,
        'assigned_quantity': assigned_quantity,
        'available_items': available_products,
        'available_quantity': max(total_quantity - assigned_quantity, 0),  # Защита от отрицательных
        'categories_stats': categories_stats,
        'popular_products': popular_products,
        'rooms_stats': rooms_stats,
        'date_stats': date_stats,
    }
    
    return render(request, 'stats/dashboard.html', context)