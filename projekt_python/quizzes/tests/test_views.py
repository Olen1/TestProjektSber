"""
Тесты для views приложения quizzes
"""
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from ..models import Submission
from ..factories import (
    QuizFactory, QuizWithQuestionsFactory
)


@pytest.fixture
def client():
    """Фикстура для Django test client"""
    return Client()


@pytest.fixture
def user():
    """Фикстура для создания пользователя"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


class TestQuizListView:
    """Тесты для view quiz_list"""
    
    def test_quiz_list_empty(self, client):
        """Тест списка тестов когда нет тестов"""
        response = client.get(reverse('quizzes:quiz_list'))
        
        assert response.status_code == 200
        assert 'quizzes' in response.context
        assert len(response.context['quizzes']) == 0
        assert 'Тестов пока нет' in response.content.decode()
    
    def test_quiz_list_with_quizzes(self, client):
        """Тест списка тестов с существующими тестами"""
        quiz1 = QuizFactory(title="Тест по математике")
        quiz2 = QuizFactory(title="Тест по физике")
        
        response = client.get(reverse('quizzes:quiz_list'))
        
        assert response.status_code == 200
        assert 'quizzes' in response.context
        quizzes = response.context['quizzes']
        assert len(quizzes) == 2
        
        # Проверяем порядок (по дате создания, новые первые)
        assert quizzes[0].title == quiz2.title
        assert quizzes[1].title == quiz1.title
    
    def test_quiz_list_template(self, client):
        """Тест использования правильного шаблона"""
        QuizFactory()
        response = client.get(reverse('quizzes:quiz_list'))
        
        assert response.status_code == 200
        assert 'quizzes/quiz_list.html' in [t.name for t in response.templates]


class TestQuizDetailView:
    """Тесты для view quiz_detail"""
    
    def test_quiz_detail_existing_quiz(self, client):
        """Тест детальной страницы существующего теста"""
        quiz = QuizWithQuestionsFactory()
        
        response = client.get(reverse('quizzes:quiz_detail', args=[quiz.id]))
        
        assert response.status_code == 200
        assert response.context['quiz'] == quiz
        assert 'questions' in response.context
        
        questions = response.context['questions']
        assert len(questions) == 3
        
        # Проверяем, что все вопросы имеют варианты ответов
        for question in questions:
            assert question.choices.count() == 4
    
    def test_quiz_detail_nonexistent_quiz(self, client):
        """Тест детальной страницы несуществующего теста"""
        response = client.get(reverse('quizzes:quiz_detail', args=[999]))
        
        assert response.status_code == 404
    
    def test_quiz_detail_template(self, client):
        """Тест использования правильного шаблона"""
        quiz = QuizFactory()
        response = client.get(reverse('quizzes:quiz_detail', args=[quiz.id]))
        
        assert response.status_code == 200
        assert 'quizzes/quiz_detail.html' in [t.name for t in response.templates]
    
    def test_quiz_detail_empty_quiz(self, client):
        """Тест детальной страницы теста без вопросов"""
        quiz = QuizFactory()
        
        response = client.get(reverse('quizzes:quiz_detail', args=[quiz.id]))
        
        assert response.status_code == 200
        assert 'Вопросов пока нет' in response.content.decode()


class TestQuizSubmitView:
    """Тесты для view quiz_submit"""
    
    def test_quiz_submit_get_redirects(self, client):
        """Тест что GET запрос перенаправляет на детальную страницу"""
        quiz = QuizFactory()
        
        response = client.get(reverse('quizzes:quiz_submit', args=[quiz.id]))
        
        assert response.status_code == 302
        assert response.url == reverse('quizzes:quiz_detail', args=[quiz.id])
    
    def test_quiz_submit_post_valid_answers(self, client):
        """Тест отправки валидных ответов"""
        quiz = QuizWithQuestionsFactory()
        
        # Получаем первый правильный ответ каждого вопроса
        correct_choices = []
        for question in quiz.questions.all():
            correct_choice = question.choices.filter(is_correct=True).first()
            correct_choices.append(correct_choice)
        
        # Формируем данные для POST запроса
        post_data = {}
        for i, choice in enumerate(correct_choices):
            post_data[f'question_{choice.question.id}'] = choice.id
        
        with patch('quizzes.views.grade_submission') as mock_grade:
            response = client.post(
                reverse('quizzes:quiz_submit', args=[quiz.id]),
                data=post_data
            )
            
            assert response.status_code == 302
            assert response.url == reverse('quizzes:quiz_detail', args=[quiz.id])
            
            # Проверяем, что создалась Submission
            submission = Submission.objects.filter(quiz=quiz).first()
            assert submission is not None
            
            # Проверяем, что создались все ответы
            answers = submission.answers.all()
            assert len(answers) == len(correct_choices)
            
            # Проверяем, что задача на проверку была отправлена
            mock_grade.send.assert_called_once_with(submission.id)
    
    def test_quiz_submit_post_invalid_choice(self, client):
        """Тест отправки с невалидным выбором"""
        quiz = QuizWithQuestionsFactory()
        
        # Отправляем несуществующий ID выбора
        post_data = {
            f'question_{quiz.questions.first().id}': 99999
        }
        
        response = client.post(
            reverse('quizzes:quiz_submit', args=[quiz.id]),
            data=post_data
        )
        
        assert response.status_code == 302
        # Проверяем, что Submission создалась, но без ответов
        submission = Submission.objects.filter(quiz=quiz).first()
        assert submission is not None
        assert submission.answers.count() == 0
    
    def test_quiz_submit_post_missing_questions(self, client):
        """Тест отправки с пропущенными вопросами"""
        quiz = QuizWithQuestionsFactory()
        
        # Отправляем только ответ на первый вопрос
        first_question = quiz.questions.first()
        first_choice = first_question.choices.first()
        
        post_data = {
            f'question_{first_question.id}': first_choice.id
        }
        
        response = client.post(
            reverse('quizzes:quiz_submit', args=[quiz.id]),
            data=post_data
        )
        
        assert response.status_code == 302
        submission = Submission.objects.filter(quiz=quiz).first()
        assert submission is not None
        # Должен быть только один ответ
        assert submission.answers.count() == 1
    
    def test_quiz_submit_post_wrong_choice_for_question(self, client):
        """Тест отправки выбора, не принадлежащего вопросу"""
        quiz = QuizWithQuestionsFactory()
        
        # Берем выбор из одного вопроса и отправляем для другого
        first_question = quiz.questions.first()
        second_question = quiz.questions.exclude(id=first_question.id).first()
        choice_from_first = first_question.choices.first()
        
        post_data = {
            f'question_{second_question.id}': choice_from_first.id
        }
        
        response = client.post(
            reverse('quizzes:quiz_submit', args=[quiz.id]),
            data=post_data
        )
        
        assert response.status_code == 302
        submission = Submission.objects.filter(quiz=quiz).first()
        assert submission is not None
        # Ответ не должен создаться, так как выбор не принадлежит вопросу
        assert submission.answers.count() == 0
    
    def test_quiz_submit_nonexistent_quiz(self, client):
        """Тест отправки ответов для несуществующего теста"""
        post_data = {'question_1': 1}
        
        response = client.post(
            reverse('quizzes:quiz_submit', args=[999]),
            data=post_data
        )
        
        assert response.status_code == 404
