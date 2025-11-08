#!/usr/bin/env python3
"""
Скрипт для запуска Django проекта с тестированием знаний
"""
import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Выполнить команду и показать результат"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - успешно")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка:")
        print(f"Код ошибки: {e.returncode}")
        if e.stdout:
            print(f"Вывод: {e.stdout}")
        if e.stderr:
            print(f"Ошибки: {e.stderr}")
        return False

def main():
    print("🚀 Запуск проекта платформы для тестирования знаний")
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists("manage.py"):
        print("❌ manage.py не найден. Запустите скрипт из корневой директории проекта.")
        sys.exit(1)
    
    # 1. Создание виртуального окружения
    if not os.path.exists(".venv"):
        if not run_command("python -m venv .venv", "Создание виртуального окружения"):
            sys.exit(1)
    
    # 2. Активация виртуального окружения и установка зависимостей
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip"
        python_cmd = ".venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Установка зависимостей"):
        sys.exit(1)
    
    # 3. Проверка Redis (опционально)
    print("\n🔍 Проверка Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis доступен")
    except Exception as e:
        print(f"⚠️  Redis недоступен: {e}")
        print("💡 Для запуска Redis используйте: docker run -p 6379:6379 --name redis -d redis:7-alpine")
        print("   Или установите Redis локально")
    
    # 4. Миграции
    if not run_command(f"{python_cmd} manage.py migrate", "Выполнение миграций Django"):
        sys.exit(1)
    
    # 5. Создание суперпользователя (опционально)
    print("\n👤 Создание суперпользователя...")
    print("   Логин: admin")
    print("   Email: admin@example.com")
    print("   Пароль: admin123")
    
    # Создаем суперпользователя через Django shell
    create_superuser_script = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь создан')
else:
    print('Суперпользователь уже существует')
"""
    
    if not run_command(f'echo "{create_superuser_script}" | {python_cmd} manage.py shell', "Создание суперпользователя"):
        print("⚠️  Не удалось создать суперпользователя, но это не критично")
    
    print("\n🎉 Проект готов к запуску!")
    print("\n📋 Инструкции по запуску:")
    print("1. Для запуска Django сервера:")
    if os.name == 'nt':
        print(f"   {python_cmd} manage.py runserver")
    else:
        print(f"   {python_cmd} manage.py runserver")
    
    print("\n2. Для запуска Dramatiq worker (в отдельном терминале):")
    if os.name == 'nt':
        print(f"   {python_cmd} -m dramatiq knowledge_platform --processes 1 --threads 4")
    else:
        print(f"   {python_cmd} -m dramatiq knowledge_platform --processes 1 --threads 4")
    
    print("\n3. Откройте в браузере:")
    print("   http://127.0.0.1:8000/ - главная страница")
    print("   http://127.0.0.1:8000/admin/ - админка (admin/admin123)")
    
    # Запускаем Django сервер
    print("\n🚀 Запуск Django сервера...")
    print("Для остановки нажмите Ctrl+C")
    try:
        subprocess.run([python_cmd, "manage.py", "runserver"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    main()

