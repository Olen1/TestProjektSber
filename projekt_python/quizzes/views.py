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

    return HttpResponseRedirect(reverse("quizzes:quiz_detail", args=[pk]))




