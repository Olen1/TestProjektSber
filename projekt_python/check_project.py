#!/usr/bin/env python3
"""
Скрипт для диагностики состояния Django проекта
"""
import os
import sys
import socket
import subprocess
from pathlib import Path

def check_port(port=8000):
    """Проверить, занят ли порт"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def check_django_setup():
    """Проверить настройку Django"""
    try:
        import django
        from django.conf import settings
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_platform.settings')
        django.setup()
        
        print("✅ Django настроен корректно")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # Проверяем базу данных
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ База данных доступна")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка настройки Django: {e}")
        return False

def check_dependencies():
    """Проверить установленные зависимости"""
    required_packages = [
        'Django', 'dramatiq', 'django_dramatiq', 'redis'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package} установлен")
        except ImportError:
            print(f"❌ {package} не установлен")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_migrations():
    """Проверить состояние миграций"""
    try:
        from django.core.management import execute_from_command_line
        
        # Проверяем не примененные миграции
        result = subprocess.run(
            ['python', 'manage.py', 'showmigrations', '--plan'],
            capture_output=True, text=True, cwd='.'
        )
        
        if result.returncode == 0:
            print("✅ Миграции проверены")
            return True
        else:
            print(f"❌ Ошибка проверки миграций: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки миграций: {e}")
        return False

def main():
    print("🔍 Диагностика Django проекта")
    print("=" * 50)
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists("manage.py"):
        print("❌ manage.py не найден. Запустите скрипт из корневой директории проекта.")
        sys.exit(1)
    
    print("📁 Рабочая директория:", os.getcwd())
    print()
    
    # Проверяем зависимости
    print("📦 Проверка зависимостей:")
    deps_ok = check_dependencies()
    print()
    
    # Проверяем настройку Django
    print("⚙️  Проверка настройки Django:")
    django_ok = check_django_setup()
    print()
    
    # Проверяем миграции
    print("🗄️  Проверка миграций:")
    migrations_ok = check_migrations()
    print()
    
    # Проверяем порт
    print("🌐 Проверка порта 8000:")
    port_in_use = check_port(8000)
    if port_in_use:
        print("✅ Порт 8000 занят (сервер запущен)")
    else:
        print("❌ Порт 8000 свободен (сервер не запущен)")
    print()
    
    # Итоговый отчет
    print("📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 30)
    
    if deps_ok and django_ok and migrations_ok:
        print("✅ Проект настроен корректно")
        
        if not port_in_use:
            print("\n🚀 Для запуска сервера выполните:")
            print("   python manage.py runserver")
        else:
            print("\n🌐 Сервер уже запущен!")
            print("   Откройте: http://127.0.0.1:8000/")
    else:
        print("❌ Обнаружены проблемы с настройкой")
        
        if not deps_ok:
            print("   • Установите зависимости: pip install -r requirements.txt")
        if not migrations_ok:
            print("   • Выполните миграции: python manage.py migrate")
    
    print("\n💡 Если проблемы продолжаются:")
    print("   1. Убедитесь, что виртуальное окружение активировано")
    print("   2. Проверьте, что Redis запущен (для Dramatiq)")
    print("   3. Используйте cmd вместо PowerShell")

if __name__ == "__main__":
    main()
