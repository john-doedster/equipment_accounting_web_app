# Django Web Application

Учёт оборудования
===
С помощью данного приложения можно вести учет оборудования на кафедре ВС. 

Возможности
====
* Возможность создавать:
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

```bash:
    1. Клонирование репозитория
```bash:
git clone https://github.com/IlyaPravilovIV121/django-web-app.git
cd django-web-app

    2. Настройка виртуального окружения
```bash:
python -m venv venv

# Активация:
# Linux/MacOS:
source venv/bin/activate

# Windows:
.\venv\Scripts\activate

    3.Установка зависимостей
```bash:
pip install -r requirements.txt

    4. Настройка окружения
Создайте файл .env на основе примера:

```bash:
cp .env.example .env
Отредактируйте .env (укажите свои SECRET_KEY, настройки БД и др.)

    5. Применение миграций
```bash:
python manage.py migrate

    6. Создание суперпользователя (опционально)
```bash:
python manage.py createsuperuser

    7. Запуск сервера
```bash:
python manage.py runserver

    8. Перейти к приложению по адресу:
http://127.0.0.1:8000