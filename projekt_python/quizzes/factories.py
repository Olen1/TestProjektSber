
import factory
from django.contrib.auth.models import User
from .models import Quiz, Question, Choice, Submission, Answer


class QuizFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Quiz
    
    title = factory.Sequence(lambda n: f"Тест {n}")
    description = factory.Faker('text', max_nb_chars=200)


class QuestionFactory(factory.django.DjangoModelFactory):

    
    class Meta:
        model = Question
    
    quiz = factory.SubFactory(QuizFactory)
    text = factory.Faker('sentence', nb_words=8)


class ChoiceFactory(factory.django.DjangoModelFactory):

    
    class Meta:
        model = Choice
    
    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker('sentence', nb_words=4)
    is_correct = False


class CorrectChoiceFactory(ChoiceFactory):

    is_correct = True


class SubmissionFactory(factory.django.DjangoModelFactory):

    
    class Meta:
        model = Submission
    
    quiz = factory.SubFactory(QuizFactory)
    score = None


class AnswerFactory(factory.django.DjangoModelFactory):

    
    class Meta:
        model = Answer
    
    submission = factory.SubFactory(SubmissionFactory)
    question = factory.SubFactory(QuestionFactory)
    choice = factory.SubFactory(ChoiceFactory)


class QuizWithQuestionsFactory(QuizFactory):

    
    @factory.post_generation
    def questions(self, create, extracted, **kwargs):
        if not create:
            return
        

        questions_count = extracted if extracted is not None else 3
        
        for i in range(questions_count):
            question = QuestionFactory(quiz=self)
            

            CorrectChoiceFactory(question=question)
            for _ in range(3):
                ChoiceFactory(question=question)
