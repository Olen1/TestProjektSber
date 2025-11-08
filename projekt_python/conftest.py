"""
Глобальные фикстуры pytest для проекта
"""
import pytest
from django.core.management import execute_from_command_line


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Настройка базы данных для тестов.
    Выполняет миграции перед запуском тестов.
    """
    with django_db_blocker.unblock():
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])


@pytest.fixture
def sample_quiz():
    """
    Фикстура для создания тестового Quiz с вопросами и вариантами ответов.
    """
    from quizzes.factories import QuizWithQuestionsFactory
    return QuizWithQuestionsFactory()


@pytest.fixture
def sample_submission():
    """
    Фикстура для создания тестовой Submission с ответами.
    """
    from quizzes.factories import (
        QuizWithQuestionsFactory, SubmissionFactory, AnswerFactory
    )
    
    quiz = QuizWithQuestionsFactory()
    submission = SubmissionFactory(quiz=quiz)
    
    # Создаем смешанные ответы (правильные и неправильные)
    questions = list(quiz.questions.all())
    
    # Первый ответ - правильный
    correct_choice = questions[0].choices.filter(is_correct=True).first()
    AnswerFactory(
        submission=submission,
        question=questions[0],
        choice=correct_choice
    )
    
    # Второй ответ - неправильный
    wrong_choice = questions[1].choices.filter(is_correct=False).first()
    AnswerFactory(
        submission=submission,
        question=questions[1],
        choice=wrong_choice
    )
    
    # Третий ответ - правильный (если есть)
    if len(questions) > 2:
        correct_choice = questions[2].choices.filter(is_correct=True).first()
        AnswerFactory(
            submission=submission,
            question=questions[2],
            choice=correct_choice
        )
    
    return submission


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Автоматически включает доступ к базе данных для всех тестов.
    """
    pass


@pytest.fixture
def mock_redis():
    """
    Фикстура для мокирования Redis в тестах.
    """
    with pytest.Mock() as mock:
        mock.ping.return_value = True
        yield mock


@pytest.fixture
def mock_dramatiq_broker():
    """
    Фикстура для мокирования Dramatiq брокера в тестах.
    """
    with pytest.patch('dramatiq.brokers.redis.RedisBroker') as mock:
        mock.return_value = pytest.Mock()
        yield mock
