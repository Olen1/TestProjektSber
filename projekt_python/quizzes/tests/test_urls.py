"""
Тесты для URL маршрутов приложения quizzes
"""
import pytest
from django.urls import reverse, resolve
from django.test import Client

from ..views import quiz_list, quiz_detail, quiz_submit


class TestQuizURLs:
    """Тесты для URL маршрутов"""
    
    def test_quiz_list_url(self):
        """Тест URL для списка тестов"""
        url = reverse('quizzes:quiz_list')
        assert url == '/'
        
        # Проверяем, что URL разрешается в правильную view
        resolved = resolve(url)
        assert resolved.func == quiz_list
    
    def test_quiz_detail_url(self):
        """Тест URL для детальной страницы теста"""
        url = reverse('quizzes:quiz_detail', args=[1])
        assert url == '/quiz/1/'
        
        # Проверяем, что URL разрешается в правильную view
        resolved = resolve(url)
        assert resolved.func == quiz_detail
        assert resolved.kwargs['pk'] == '1'
    
    def test_quiz_submit_url(self):
        """Тест URL для отправки ответов"""
        url = reverse('quizzes:quiz_submit', args=[1])
        assert url == '/quiz/1/submit/'
        
        # Проверяем, что URL разрешается в правильную view
        resolved = resolve(url)
        assert resolved.func == quiz_submit
        assert resolved.kwargs['pk'] == '1'
    
    def test_quiz_urls_accessible(self):
        """Тест доступности всех URL"""
        client = Client()
        
        # Список тестов должен быть доступен
        response = client.get(reverse('quizzes:quiz_list'))
        assert response.status_code == 200
        
        # Детальная страница несуществующего теста должна возвращать 404
        response = client.get(reverse('quizzes:quiz_detail', args=[999]))
        assert response.status_code == 404
        
        # GET запрос на submit должен перенаправлять
        response = client.get(reverse('quizzes:quiz_submit', args=[999]))
        assert response.status_code == 302
    
    def test_url_namespace(self):
        """Тест что все URL используют правильный namespace"""
        urls = [
            'quizzes:quiz_list',
            'quizzes:quiz_detail',
            'quizzes:quiz_submit'
        ]
        
        for url_name in urls:
            url = reverse(url_name, args=[1] if 'detail' in url_name or 'submit' in url_name else [])
            assert url is not None
            assert url.startswith('/')
