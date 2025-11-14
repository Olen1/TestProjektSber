
import pytest
from django.urls import reverse, resolve
from ..views import quiz_list, quiz_detail, quiz_submit


class TestQuizURLs:
    """Тесты для URL приложения quizzes"""

    def test_quiz_list_url(self):
        """Тест URL для списка тестов"""
        url = reverse('quizzes:quiz_list')
        assert url == '/'


        resolved = resolve(url)
        assert resolved.func == quiz_list
        assert resolved.view_name == 'quizzes:quiz_list'

    def test_quiz_detail_url(self):
        """Тест URL для детальной страницы теста"""
        url = reverse('quizzes:quiz_detail', args=[1])
        assert url == '/quiz/1/'


        resolved = resolve(url)
        assert resolved.func == quiz_detail
        assert resolved.view_name == 'quizzes:quiz_detail'
        assert resolved.kwargs['pk'] == 1

    def test_quiz_submit_url(self):
        """Тест URL для отправки ответов"""
        url = reverse('quizzes:quiz_submit', args=[1])
        assert url == '/quiz/1/submit/'


        resolved = resolve(url)
        assert resolved.func == quiz_submit
        assert resolved.view_name == 'quizzes:quiz_submit'
        assert resolved.kwargs['pk'] == 1

