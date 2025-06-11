from django.shortcuts import render
from django.db.models import Count, Sum, Q
from equipment.models import Products, Categories
from orders.models import OrderItem, Order
from collections import defaultdict
from datetime import datetime, timedelta

def equipment_statistics(request):
    # Основные показатели
    total_products = Products.objects.count()
    total_quantity = Products.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Статистика по закрепленному оборудованию
    assigned_items = OrderItem.objects.count()
    assigned_quantity = OrderItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Статистика по категориям
    categories_stats = (
        Products.objects
        .values('category__name')
        .annotate(
            total=Count('id'),
            total_qty=Sum('quantity'),
            assigned=Count('orderitem'),
            assigned_qty=Sum('orderitem__quantity')
        )
        .order_by('-total_qty')
    )
    
    # Топ товаров по количеству
    popular_products = (
        Products.objects
        .annotate(
            assigned_count=Count('orderitem'),
            assigned_qty=Sum('orderitem__quantity')
        )
        .order_by('-quantity')[:10]
    )
    
    # Статистика по кабинетам
    rooms_stats = (
        Order.objects
        .exclude(office__isnull=True)
        .exclude(office='')
        .values('office')
        .annotate(
            equipment_count=Count('orderitem'),
            total_quantity=Sum('orderitem__quantity')
        )
        .order_by('-equipment_count')[:10]
    )
    
    # Динамика выдачи за последние 30 дней
    date_stats = []
    for i in range(30, -1, -1):
        date = (datetime.now() - timedelta(days=i)).date()
        assigned = Order.objects.filter(
            created_timestamp__date=date
        ).aggregate(
            count=Count('id'),
            qty=Sum('orderitem__quantity')
        )
        
        returned = Order.objects.filter(
            orderitem__created_timestamp__date=date,
            status__icontains='возврат'
        ).aggregate(
            count=Count('id'),
            qty=Sum('orderitem__quantity')
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
        'available_items': total_products - assigned_items,
        'available_quantity': total_quantity - assigned_quantity,
        'categories_stats': categories_stats,
        'popular_products': popular_products,
        'rooms_stats': rooms_stats,
        'date_stats': date_stats,
    }
    
    return render(request, 'stats/dashboard.html', context)