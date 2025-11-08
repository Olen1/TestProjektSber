# Платформа для тестирования знаний (Django + Dramatiq)

Базовый шаблон проекта: Django-приложение с приложением `quizzes`, Dramatiq-задачей для асинхронной проверки ответов и Redis-брокером.

## Требования

- Python 3.10+
- Redis (локально или в Docker)

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

Откройте `http://127.0.0.1:8000/` — список тестов. Админка: `http://127.0.0.1:8000/admin/`.

## Тестирование

```powershell
# Запуск всех тестов
python -m pytest -v

# Запуск с покрытием кода
python -m pytest --cov=quizzes --cov-report=html -v

# Запуск конкретного теста
python -m pytest quizzes/tests/test_models.py -v

# Запуск через скрипт
python run_tests.py
```

## Структура

```
.
├── manage.py
├── knowledge_platform/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── quizzes/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── factories.py
│   ├── models.py
│   ├── tasks.py
│   ├── urls.py
│   ├── views.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       ├── test_tasks.py
│       └── test_urls.py
├── templates/
│   └── quizzes/
│       ├── quiz_detail.html
│       └── quiz_list.html
├── requirements.txt
├── pytest.ini
├── conftest.py
├── run_tests.py
├── .gitignore
└── app.py  # пример скрипта вне Django
```

## Как это работает

- `quizzes` хранит тесты, вопросы и варианты.
- При отправке ответов создаётся `Submission`, после чего Dramatiq-актер `grade_submission` асинхронно считает балл и сохраняет его.



