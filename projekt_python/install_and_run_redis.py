#!/usr/bin/env python3
"""
Скрипт для установки и запуска Redis
"""
import os
import sys
import subprocess
import socket
import time


def check_docker():
    """Проверить, установлен ли Docker"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker найден: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker не найден")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker не установлен или не доступен")
        return False


def check_redis_port():
    """Проверить, запущен ли Redis на порту 6379"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 6379))
        sock.close()
        return result == 0
    except:
        return False


def stop_existing_redis():
    """Остановить существующий контейнер Redis"""
    try:
        print("🔄 Останавливаем существующий Redis контейнер...")
        subprocess.run(['docker', 'stop', 'redis'], 
                      capture_output=True, text=True, timeout=10)
        subprocess.run(['docker', 'rm', 'redis'], 
                      capture_output=True, text=True, timeout=10)
        print("✅ Старый контейнер удален")
    except Exception as e:
        print(f"⚠️  Не удалось остановить старый контейнер: {e}")


def start_redis_container():
    """Запустить Redis в Docker контейнере"""
    try:
        print("🚀 Запускаем Redis в Docker...")
        
        # Команда для запуска Redis
        cmd = [
            'docker', 'run', 
            '-d',  # в фоновом режиме
            '--name', 'redis',
            '-p', '6379:6379',
            'redis:7-alpine'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Redis контейнер запущен успешно!")
            print(f"   Container ID: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Ошибка запуска Redis: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при запуске Redis")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def wait_for_redis():
    """Ждать, пока Redis станет доступен"""
    print("⏳ Ожидаем запуска Redis...")
    
    for i in range(30):  # ждем до 30 секунд
        if check_redis_port():
            print("✅ Redis доступен!")
            return True
        time.sleep(1)
        if i % 5 == 0 and i > 0:
            print(f"   ... еще ждем ({i}/30)")
    
    print("❌ Redis не стал доступен за 30 секунд")
    return False


def test_redis_connection():
    """Тестировать подключение к Redis"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Подключение к Redis работает!")
        
        # Тестовые операции
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        if value == b'test_value':
            print("✅ Тестовые операции Redis работают!")
            r.delete('test_key')
        else:
            print("⚠️  Тестовые операции Redis не работают")
        
        return True
    except ImportError:
        print("⚠️  Модуль redis не установлен (pip install redis)")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Redis: {e}")
        return False


def main():
    print("🔧 Установка и запуск Redis для Django проекта")
    print("=" * 60)
    
    # Проверяем Docker
    print("\n📦 Проверка Docker:")
    if not check_docker():
        print("\n💡 Для установки Docker:")
        print("   1. Скачайте Docker Desktop с https://www.docker.com/products/docker-desktop/")
        print("   2. Установите и перезагрузите компьютер")
        print("   3. Запустите Docker Desktop")
        print("\n🔄 Альтернатива - установка Redis напрямую:")
        print("   Скачайте с https://github.com/microsoftarchive/redis/releases")
        return False
    
    # Останавливаем старый контейнер
    print("\n🛑 Остановка старых контейнеров:")
    stop_existing_redis()
    
    # Проверяем, не запущен ли уже Redis
    if check_redis_port():
        print("✅ Redis уже запущен на порту 6379")
        if test_redis_connection():
            print("🎉 Redis готов к использованию!")
            return True
    
    # Запускаем новый контейнер
    print("\n🚀 Запуск Redis:")
    if not start_redis_container():
        return False
    
    # Ждем запуска
    if not wait_for_redis():
        return False
    
    # Тестируем подключение
    print("\n🧪 Тестирование подключения:")
    if test_redis_connection():
        print("\n🎉 Redis успешно установлен и запущен!")
        print("\n📋 Информация:")
        print("   • Адрес: localhost:6379")
        print("   • Контейнер: redis")
        print("   • Команды управления:")
        print("     - Остановить: docker stop redis")
        print("     - Запустить: docker start redis")
        print("     - Удалить: docker rm -f redis")
        return True
    else:
        print("\n❌ Redis запущен, но есть проблемы с подключением")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Установка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)
