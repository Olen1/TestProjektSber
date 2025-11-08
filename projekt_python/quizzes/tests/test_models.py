"""
Тесты для моделей приложения quizzes
"""
import pytest
from django.db import IntegrityError

from .factories import (
    QuizFactory, QuestionFactory, ChoiceFactory, CorrectChoiceFactory,
    SubmissionFactory, AnswerFactory, QuizWithQuestionsFactory
)


class TestQuizModel:
    """Тесты для модели Quiz"""
    
    def test_quiz_creation(self):
        """Тест создания Quiz"""
        quiz = QuizFactory(title="Тест по математике")
        assert quiz.title == "Тест по математике"
        assert quiz.description is not None
        assert quiz.created_at is not None
    
    def test_quiz_str(self):
        """Тест строкового представления Quiz"""
        quiz = QuizFactory(title="Тест по физике")
        assert str(quiz) == "Тест по физике"
    
    def test_quiz_questions_relationship(self):
        """Тест связи Quiz с Question"""
        quiz = QuizFactory()
        question1 = QuestionFactory(quiz=quiz)
        question2 = QuestionFactory(quiz=quiz)
        
        assert quiz.questions.count() == 2
        assert question1 in quiz.questions.all()
        assert question2 in quiz.questions.all()
    
    def test_quiz_submissions_relationship(self):
        """Тест связи Quiz с Submission"""
        quiz = QuizFactory()
        submission1 = SubmissionFactory(quiz=quiz)
        submission2 = SubmissionFactory(quiz=quiz)
        
        assert quiz.submissions.count() == 2
        assert submission1 in quiz.submissions.all()
        assert submission2 in quiz.submissions.all()


class TestQuestionModel:
    """Тесты для модели Question"""
    
    def test_question_creation(self):
        """Тест создания Question"""
        quiz = QuizFactory()
        question = QuestionFactory(quiz=quiz, text="Сколько будет 2+2?")
        
        assert question.quiz == quiz
        assert question.text == "Сколько будет 2+2?"
    
    def test_question_str(self):
        """Тест строкового представления Question"""
        question = QuestionFactory(text="Длинный вопрос с множеством слов")
        assert str(question) == "Длинный вопрос с множеством слов"[:50]
    
    def test_question_choices_relationship(self):
        """Тест связи Question с Choice"""
        question = QuestionFactory()
        choice1 = ChoiceFactory(question=question)
        choice2 = ChoiceFactory(question=question)
        
        assert question.choices.count() == 2
        assert choice1 in question.choices.all()
        assert choice2 in question.choices.all()


class TestChoiceModel:
    """Тесты для модели Choice"""
    
    def test_choice_creation(self):
        """Тест создания Choice"""
        question = QuestionFactory()
        choice = ChoiceFactory(
            question=question, 
            text="Вариант ответа", 
            is_correct=True
        )
        
        assert choice.question == question
        assert choice.text == "Вариант ответа"
        assert choice.is_correct is True
    
    def test_choice_str(self):
        """Тест строкового представления Choice"""
        choice = ChoiceFactory(text="Длинный вариант ответа с множеством слов")
        assert str(choice) == "Длинный вариант ответа с множеством слов"[:50]
    
    def test_correct_choice_factory(self):
        """Тест фабрики для правильного ответа"""
        choice = CorrectChoiceFactory()
        assert choice.is_correct is True


class TestSubmissionModel:
    """Тесты для модели Submission"""
    
    def test_submission_creation(self):
        """Тест создания Submission"""
        quiz = QuizFactory()
        submission = SubmissionFactory(quiz=quiz)
        
        assert submission.quiz == quiz
        assert submission.created_at is not None
        assert submission.score is None
    
    def test_submission_str(self):
        """Тест строкового представления Submission"""
        quiz = QuizFactory(title="Тест")
        submission = SubmissionFactory(quiz=quiz)
        assert "Submission" in str(submission)
        assert "Тест" in str(submission)
    
    def test_submission_answers_relationship(self):
        """Тест связи Submission с Answer"""
        submission = SubmissionFactory()
        answer1 = AnswerFactory(submission=submission)
        answer2 = AnswerFactory(submission=submission)
        
        assert submission.answers.count() == 2
        assert answer1 in submission.answers.all()
        assert answer2 in submission.answers.all()


class TestAnswerModel:
    """Тесты для модели Answer"""
    
    def test_answer_creation(self):
        """Тест создания Answer"""
        submission = SubmissionFactory()
        question = QuestionFactory()
        choice = ChoiceFactory(question=question)
        
        answer = AnswerFactory(
            submission=submission,
            question=question,
            choice=choice
        )
        
        assert answer.submission == submission
        assert answer.question == question
        assert answer.choice == choice
    
    def test_answer_str(self):
        """Тест строкового представления Answer"""
        answer = AnswerFactory()
        assert "Answer" in str(answer)
    
    def test_answer_unique_constraint(self):
        """Тест уникальности ответа на вопрос в рамках одной попытки"""
        submission = SubmissionFactory()
        question = QuestionFactory()
        choice1 = ChoiceFactory(question=question)
        choice2 = ChoiceFactory(question=question)
        
        # Создаем первый ответ
        AnswerFactory(submission=submission, question=question, choice=choice1)
        
        # Попытка создать второй ответ на тот же вопрос должна вызвать ошибку
        with pytest.raises(IntegrityError):
            AnswerFactory(submission=submission, question=question, choice=choice2)


class TestQuizWithQuestionsFactory:
    """Тесты для фабрики QuizWithQuestionsFactory"""
    
    def test_quiz_with_questions_creation(self):
        """Тест создания Quiz с вопросами и вариантами ответов"""
        quiz = QuizWithQuestionsFactory()
        
        assert quiz.questions.count() == 3
        
        for question in quiz.questions.all():
            assert question.choices.count() == 4
            # Проверяем, что есть ровно один правильный ответ
            correct_choices = question.choices.filter(is_correct=True)
            assert correct_choices.count() == 1
    
    def test_quiz_with_custom_questions_count(self):
        """Тест создания Quiz с заданным количеством вопросов"""
        quiz = QuizWithQuestionsFactory(questions=5)
        
        assert quiz.questions.count() == 5
    
    def test_quiz_with_zero_questions(self):
        """Тест создания Quiz без вопросов"""
        quiz = QuizWithQuestionsFactory(questions=0)
        
        assert quiz.questions.count() == 0
