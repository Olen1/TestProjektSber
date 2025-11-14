from __future__ import annotations
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Quiz, Question, Choice, Submission, Answer


def quiz_list(request: HttpRequest) -> HttpResponse:
    quizzes = Quiz.objects.order_by("-created_at")
    return render(request, "quizzes/quiz_list.html", {"quizzes": quizzes})


def quiz_detail(request: HttpRequest, pk: int) -> HttpResponse:
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related("choices").all()
    return render(request, "quizzes/quiz_detail.html", {"quiz": quiz, "questions": questions})


def quiz_submit(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("quizzes:quiz_detail", pk=pk)

    quiz = get_object_or_404(Quiz, pk=pk)
    submission = Submission.objects.create(quiz=quiz)

    for question in quiz.questions.all():
        choice_id = request.POST.get(f"question_{question.id}")
        if not choice_id:
            continue
        try:
            choice = Choice.objects.get(id=int(choice_id), question=question)
        except (Choice.DoesNotExist, ValueError):
            continue
        Answer.objects.create(submission=submission, question=question, choice=choice)

    from .tasks import grade_submission
    grade_submission.send(submission.id)


    return HttpResponseRedirect(reverse("quizzes:quiz_results", args=[submission.id]))


def quiz_results(request: HttpRequest, submission_id: int) -> HttpResponse:
    submission = get_object_or_404(
        Submission.objects.select_related('quiz'),
        id=submission_id
    )


    answers = submission.answers.select_related('question', 'choice').all()

    correct_answers = sum(1 for answer in answers if answer.choice.is_correct)
    total_questions = submission.quiz.questions.count()

    if submission.score is None:
        submission.score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        submission.save()

    context = {
        'submission': submission,
        'quiz': submission.quiz,
        'answers': answers,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'percentage': submission.score,
    }

    return render(request, "quizzes/quiz_results.html", context)