# 🚀 Блог 2.0
 
Веб-приложение для ведения личного блога с системой авторизации и комментариями. Проект выполнен в Django с использованием представлений на основе классов - Class-Based Views, CBV.

## 🛠 Технологии и стек
* **Backend:** Python 3.11.3, Django 5.2.13
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
* **Database:** PostgreSQL

## 📦 Инструкция по локальному запуску

Следуйте этим шагам, чтобы запустить проект на своем компьютере.

### 1. Клонирование репозитория
```bash
git clone git@github.com:Vladimir-P8/blog_cbv.git
cd blog_cbv
```

### 2. Настройка виртуального окружения
```bash
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для macOS/Linux:
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Применение миграций базы данных
```bash
python manage.py migrate
```

### 5. Создание суперпользователя (администратора)
```bash
python manage.py createsuperuser
```

### 6. Запуск сервера разработки
```bash
python manage.py runserver
```
Теперь проект доступен в браузере по адресу: [https:gadzin.ru](https://gadzin.ru/)

## 📂 Структура проекта
* `core/` — основные настройки Django-проекта.
* `templates/` — глобальные HTML-шаблоны.
* `static/` — стили CSS, изображения и JS-скрипты.
