# Платформа для тестирования знаний (Django + Dramatiq)

Базовый шаблон проекта: Django-приложение с приложением `quizzes`, Dramatiq-задачей для асинхронной проверки ответов и Redis-брокером.

## Установка (Windows PowerShell)

```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Redis

- Вариант 1 (Docker):

```powershell
docker run -p 6379:6379 --name redis -d redis:7-alpine
```

- Вариант 2: Установить Redis нативно и запустить на `localhost:6379`.

## Миграции и суперпользователь

```powershell
python manage.py migrate
python manage.py createsuperuser
```

## Запуск

В одном терминале:

```powershell
python manage.py runserver
```

В другом терминале (активируйте venv):

```powershell
python -m dramatiq knowledge_platform --processes 1 --threads 4
```

Откройте `http://127.0.0.1:8000/login/` — список тестов. 
Админка: `http://127.0.0.1:8000/admin/`.

