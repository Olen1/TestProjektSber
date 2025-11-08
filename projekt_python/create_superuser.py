#!/usr/bin/env python3
"""
Скрипт для создания суперпользователя Django
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    """Создать суперпользователя если он не существует"""
    User = get_user_model()
    
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'
    
    # Проверяем, существует ли пользователь
    if User.objects.filter(username=username).exists():
        print(f"✅ Суперпользователь '{username}' уже существует")
        
        # Обновляем пароль на всякий случай
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"🔄 Пароль для '{username}' обновлен на '{password}'")
        
    else:
        # Создаем нового суперпользователя
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Суперпользователь '{username}' создан успешно!")
        print(f"📧 Email: {email}")
        print(f"🔑 Пароль: {password}")
    
    print("\n🌐 Теперь вы можете войти в админку:")
    print("   URL: http://127.0.0.1:8000/admin/")
    print(f"   Логин: {username}")
    print(f"   Пароль: {password}")

if __name__ == "__main__":
    try:
        create_superuser()
    except Exception as e:
        print(f"❌ Ошибка создания суперпользователя: {e}")
        sys.exit(1)
