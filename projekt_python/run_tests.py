#!/usr/bin/env python3
"""
Скрипт для запуска тестов проекта
"""
import os
import sys
import subprocess
from pathlib import Path


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
    print("🧪 Запуск тестов для проекта платформы тестирования знаний")
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists("manage.py"):
        print("❌ manage.py не найден. Запустите скрипт из корневой директории проекта.")
        sys.exit(1)
    
    # Определяем команды в зависимости от ОС
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip"
        python_cmd = ".venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    # Проверяем, что виртуальное окружение существует
    if not os.path.exists(".venv"):
        print("❌ Виртуальное окружение не найдено. Сначала создайте его:")
        print("   python -m venv .venv")
        print("   .venv\\Scripts\\activate.bat  # Windows")
        print("   source .venv/bin/activate     # Linux/Mac")
        sys.exit(1)
    
    # Устанавливаем зависимости для тестирования
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Установка зависимостей"):
        print("⚠️  Попробуйте установить зависимости вручную")
    
    # Запускаем тесты
    print("\n🚀 Запуск тестов...")
    
    # Различные варианты запуска тестов
    test_commands = [
        # Все тесты
        f"{python_cmd} -m pytest -v",
        
        # Тесты с покрытием кода
        f"{python_cmd} -m pytest --cov=quizzes --cov-report=html --cov-report=term-missing -v",
        
        # Только быстрые тесты
        f"{python_cmd} -m pytest -m 'not slow' -v",
        
        # Тесты конкретного модуля
        f"{python_cmd} -m pytest quizzes/tests/test_models.py -v",
        
        # Тесты с детальным выводом
        f"{python_cmd} -m pytest -s --tb=short -v",
    ]
    
    print("\n📋 Доступные команды для запуска тестов:")
    for i, cmd in enumerate(test_commands, 1):
        print(f"{i}. {cmd}")
    
    print("\n💡 Примеры запуска:")
    print("1. Все тесты: pytest -v")
    print("2. С покрытием: pytest --cov=quizzes --cov-report=html -v")
    print("3. Только модели: pytest quizzes/tests/test_models.py -v")
    print("4. Конкретный тест: pytest quizzes/tests/test_models.py::TestQuizModel::test_quiz_creation -v")
    
    # Запускаем базовые тесты
    print("\n🧪 Запуск базовых тестов...")
    try:
        subprocess.run([python_cmd, "-m", "pytest", "-v", "--tb=short"], check=True)
        print("\n✅ Все тесты прошли успешно!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Некоторые тесты не прошли. Код ошибки: {e.returncode}")
        print("💡 Проверьте вывод выше для деталей")
    except KeyboardInterrupt:
        print("\n👋 Запуск тестов прерван пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска тестов: {e}")


if __name__ == "__main__":
    main()
