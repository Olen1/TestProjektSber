"""
Тесты для Dramatiq задач приложения quizzes
"""
import pytest
from unittest.mock import patch, MagicMock

from ..models import Submission
from ..tasks import grade_submission
from ..factories import  (
    QuizWithQuestionsFactory, SubmissionFactory, AnswerFactory,
    CorrectChoiceFactory, ChoiceFactory
)


class TestGradeSubmissionTask:
    """Тесты для задачи grade_submission"""
    
    def test_grade_submission_all_correct(self):
        """Тест подсчета баллов когда все ответы правильные"""
        quiz = QuizWithQuestionsFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        # Создаем правильные ответы на все вопросы
        for question in quiz.questions.all():
            correct_choice = question.choices.filter(is_correct=True).first()
            AnswerFactory(
                submission=submission,
                question=question,
                choice=correct_choice
            )
        
        # Вызываем задачу напрямую
        grade_submission(submission.id)
        
        # Проверяем результат
        submission.refresh_from_db()
        assert submission.score == 3  # Все 3 ответа правильные
    
    def test_grade_submission_all_wrong(self):
        """Тест подсчета баллов когда все ответы неправильные"""
        quiz = QuizWithQuestionsFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        # Создаем неправильные ответы на все вопросы
        for question in quiz.questions.all():
            wrong_choice = question.choices.filter(is_correct=False).first()
            AnswerFactory(
                submission=submission,
                question=question,
                choice=wrong_choice
            )
        
        # Вызываем задачу напрямую
        grade_submission(submission.id)
        
        # Проверяем результат
        submission.refresh_from_db()
        assert submission.score == 0  # Ни одного правильного ответа
    
    def test_grade_submission_partial_correct(self):
        """Тест подсчета баллов когда часть ответов правильные"""
        quiz = QuizWithQuestionsFactory()
        submission = SubmissionFactory(quiz=quiz)
        
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
        
        # Третий ответ - правильный
        correct_choice = questions[2].choices.filter(is_correct=True).first()
        AnswerFactory(
            submission=submission,
            question=questions[2],
            choice=correct_choice
        )
        
        # Вызываем задачу напрямую
        grade_submission(submission.id)
        
        # Проверяем результат
        submission.refresh_from_db()
        assert submission.score == 2  # 2 правильных ответа из 3
    
    def test_grade_submission_no_answers(self):
        """Тест подсчета баллов когда нет ответов"""
        quiz = QuizFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        # Вызываем задачу напрямую
        grade_submission(submission.id)
        
        # Проверяем результат
        submission.refresh_from_db()
        assert submission.score == 0  # Нет ответов
    
    def test_grade_submission_database_transaction(self):
        """Тест что задача выполняется в транзакции"""
        quiz = QuizWithQuestionsFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        # Создаем правильный ответ
        question = quiz.questions.first()
        correct_choice = question.choices.filter(is_correct=True).first()
        AnswerFactory(
            submission=submission,
            question=question,
            choice=correct_choice
        )
        
        with patch('quizzes.tasks.transaction.atomic') as mock_transaction:
            mock_context = MagicMock()
            mock_transaction.return_value.__enter__ = MagicMock(return_value=mock_context)
            mock_transaction.return_value.__exit__ = MagicMock(return_value=None)
            
            grade_submission(submission.id)
            
            # Проверяем, что использовалась транзакция
            mock_transaction.assert_called_once()
    
    def test_grade_submission_submission_not_found(self):
        """Тест обработки случая когда Submission не найдена"""
        with pytest.raises(Submission.DoesNotExist):
            grade_submission(99999)  # Несуществующий ID
    
    def test_grade_submission_select_for_update(self):
        """Тест использования select_for_update"""
        quiz = QuizFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        with patch('quizzes.tasks.Submission.objects.select_for_update') as mock_select:
            mock_submission = MagicMock()
            mock_submission.answers.select_related.return_value.all.return_value = []
            mock_select.return_value.get.return_value = mock_submission
            
            grade_submission(submission.id)
            
            # Проверяем, что использовался select_for_update
            mock_select.assert_called_once()
            mock_select.return_value.get.assert_called_once_with(id=submission.id)
    
    def test_grade_submission_updates_score_field(self):
        """Тест что обновляется только поле score"""
        quiz = QuizWithQuestionsFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        # Создаем правильный ответ
        question = quiz.questions.first()
        correct_choice = question.choices.filter(is_correct=True).first()
        AnswerFactory(
            submission=submission,
            question=question,
            choice=correct_choice
        )
        
        with patch.object(Submission, 'save') as mock_save:
            grade_submission(submission.id)
            
            # Проверяем, что save вызван с update_fields
            mock_save.assert_called_once_with(update_fields=['score'])
    
    def test_grade_submission_with_mixed_question_types(self):
        """Тест подсчета баллов с вопросами разного типа"""
        quiz = QuizFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        # Создаем вопросы с разным количеством вариантов ответов
        question1 = QuestionFactory(quiz=quiz, text="Вопрос 1")
        question2 = QuestionFactory(quiz=quiz, text="Вопрос 2")
        
        # Для первого вопроса создаем 2 варианта (1 правильный)
        CorrectChoiceFactory(question=question1, text="Правильный")
        ChoiceFactory(question=question1, text="Неправильный")
        
        # Для второго вопроса создаем 4 варианта (1 правильный)
        CorrectChoiceFactory(question=question2, text="Правильный")
        ChoiceFactory(question=question2, text="Неправильный 1")
        ChoiceFactory(question=question2, text="Неправильный 2")
        ChoiceFactory(question=question2, text="Неправильный 3")
        
        # Создаем правильные ответы
        AnswerFactory(
            submission=submission,
            question=question1,
            choice=question1.choices.filter(is_correct=True).first()
        )
        AnswerFactory(
            submission=submission,
            question=question2,
            choice=question2.choices.filter(is_correct=True).first()
        )
        
        # Вызываем задачу
        grade_submission(submission.id)
        
        # Проверяем результат
        submission.refresh_from_db()
        assert submission.score == 2  # Оба ответа правильные


class TestTaskIntegration:
    """Интеграционные тесты для задач"""
    
    def test_task_can_be_sent_to_broker(self):
        """Тест что задача может быть отправлена в брокер"""
        quiz = QuizWithQuestionsFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        # Проверяем, что задача может быть отправлена (не вызывается сразу)
        task_result = grade_submission.send(submission.id)
        
        # Проверяем, что получили объект задачи
        assert task_result is not None
        assert hasattr(task_result, 'message_id')
    
    def test_task_with_invalid_submission_id(self):
        """Тест отправки задачи с невалидным ID"""
        # Это не должно вызывать исключение при отправке
        task_result = grade_submission.send(99999)
        assert task_result is not None
