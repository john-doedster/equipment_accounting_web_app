from django.http import HttpResponse
from django.shortcuts import render

from equipment.models import Categories

def index(request):

    categories = Categories.objects.all()


    context = {
        'title': 'Equip - Главная страница',
        'content': "Equipment app for SibSUTIS", 
        'categories': categories
    }
    return render(request, 'main/index.html', context)

def about(request):
    return HttpResponse('about')

def about(request):
    context = {
        'title': 'Equip - About us ',
        'content': "About us",
        'text_on_page': "Данное приложение разработано в рамках ВКР Правиловым Ильёй студентом группы ИВ-121 для кафедры ВС"
    }
    return render(request, 'main/about.html', context)

