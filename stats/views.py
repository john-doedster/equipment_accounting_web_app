from django.shortcuts import render
from django.db.models import Count, Sum
from equipment.models import Products, Categories
from collections import defaultdict
from datetime import datetime, timedelta

def equipment_statistics(request):
    # Основные показатели
    total = Products.objects.count()
    total_quantity = Products.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Статистика по категориям
    categories_stats = (
        Products.objects
        .values('category__name')
        .annotate(
            total=Count('id'),
            total_qty=Sum('quantity')
        )
        .order_by('-total_qty')
    )
    
    # Топ товаров по количеству
    popular_products = (
        Products.objects
        .order_by('-quantity')[:10]
    )
    
    context = {
        'title': 'Статистика',
        'total': total,
        'total_quantity': total_quantity,
        'categories_stats': categories_stats,
        'popular_products': popular_products,
    }
    
    return render(request, 'stats/dashboard.html', context)

# def export_stats(request):
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename=equipment_stats.xlsx'
    
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Статистика"
    
#     # Заголовки
#     ws.append(['Категория', 'Всего', 'Закреплено', 'Доступно'])
    
#     # Данные
#     for cat in categories_stats:
#         ws.append([cat['category__name'], cat['total'], cat['assigned'], cat['total'] - cat['assigned']])
    
#     wb.save(response)
#     return response
