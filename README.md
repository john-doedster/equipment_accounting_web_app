# Django Web Application for equipment accounting

Для чего
===
С помощью данного приложения можно вести учет оборудования на кафедре ВС 

Возможности
====
Возможность создавать:
* Производителя
* Тип оборудования
* Место расположение
* Модель оборудования
* Серийный номер
* Статус оборудования
* Редактировать добавленное оборудование
* Выбирать оборудование из предложенного асортимента
* Вести точный учёт оборудования


## 🛠 Технологии
- Python 3.13.2
- Django 5.1
- PostgreSQL


## ⚡ Главный экран веб-приложения

![Главный экран веб-приложения](./screenshots/main_page.png)


### Предварительные требования
- Установленный Python 3.9+
- Установленный Git
- PostgreSQL


📦 Установка и запуск

| Шаг | Действие | Команда |
|-----|----------|---------|
| 1️⃣ | Клонирование | `git clone https://github.com/john-doedster/equipment_accounting_web_app.git` |
| 2️⃣ | Переход в папку | `cd django-web-app` |
| 3️⃣ | Создание venv | `python -m venv venv` |
| 4️⃣ | Активация venv (Win) | `venv\Scripts\activate` |
| 4️⃣ | Активация venv (Mac/Linux) | `source venv/bin/activate` |
| 5️⃣ | Установка зависимостей | `pip install -r requirements.txt` |
| 6️⃣ | Миграции | `python manage.py migrate` |
| 7️⃣ | Запуск | `python manage.py runserver` |

🌐 После запуска: http://127.0.0.1:8000
