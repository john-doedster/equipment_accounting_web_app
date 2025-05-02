from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from equipment.models import Categories


def index(request):

    context = {
        'title': 'УЧЁТКА',
        'APP_NAME': 'Учётка',  # Название вашего приложения
    }
    return render(request, 'main/index.html', context)


def about(request):
    return HttpResponse('about')

def about(request):
    context = {
        'title': 'О проекте',
        'content': "Информация",
        'features': [
            {
                'icon': 'fa-automobile',
                'title': 'Автоматизация учёта',
                'description': 'Замена бумажных журналов и сложных таблиц'
            },
            {
                'icon': 'fa-chart-line',
                'title': 'Прозрачность данных',
                'description': 'Вся информация доступна в реальном времени'
            },
            {
                'icon': 'fa-clock',
                'title': 'Экономия времени',
                'description': 'Быстрый поиск, фильтрация и отчетность'
            },
            {
                'icon': 'fa-heartbeat',
                'title': 'Контроль состояния',
                'description': 'Своевременное обслуживание оборудования'
            }
        ],
        'user_roles': [
            {
                'icon': 'fa-user-graduate',
                'title': 'Преподаватели',
                'description': 'Учёт закрепленного оборудования'
            },
            {
                'icon': 'fa-tools',
                'title': 'Технические специалисты',
                'description': 'Мониторинг состояния и ремонтов'
            },
            {
                'icon': 'fa-user-tie',
                'title': 'Администрация',
                'description': 'Аналитика и планирование закупок'
            }
        ],
        'text_on_page': mark_safe("""
            <p class='lead'>Мы рады приветствовать вас в нашем веб-приложении для учёта оборудования!</p>
            <p>Наша система создана для удобного управления IT-активами кафедры: компьютерами, серверами и сетевым оборудованием.</p>
        """)
    }
    return render(request, 'main/about.html', context)


def contacts(request):
    context = {
        'title': 'Контакты',
        'content': "Контактная информация",
        'text_on_page': mark_safe("""
            <h3>Наши контакты</h3>
            <p><strong>Адрес:</strong> г. Москва, ул. Примерная, д. 123</p>
            <p><strong>Телефон:</strong> +7 (495) 123-45-67</p>
            <p><strong>Email:</strong> info@example.com</p>
            <p><strong>Режим работы:</strong> Пн-Пт: 9:00 - 18:00</p>
            
            <h4 class="mt-4">Отдел технической поддержки</h4>
            <p>Телефон: +7 (495) 765-43-21</p>
            <p>Email: support@example.com</p>
        """)
    }
    return render(request, 'main/contacts.html', context)

