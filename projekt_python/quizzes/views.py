# quizzes/views.py
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect

from .models import Quiz, Submission, Question, Choice, Answer


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz})


def calculate_score(post_data, quiz, submission):
    total_questions = quiz.questions.count()
    if total_questions == 0:
        return 0.0

    correct_count = 0
    answers_to_create = []

    for question in quiz.questions.all():
        choice_id = post_data.get(f"question_{question.id}")
        if choice_id and choice_id.isdigit():
            try:
                selected_choice = Choice.objects.get(id=int(choice_id), question=question)
                if selected_choice.is_correct:
                    correct_count += 1
                answers_to_create.append(
                    Answer(submission=submission, question=question, choice=selected_choice)
                )
            except Choice.DoesNotExist:
                pass

    if answers_to_create:
        Answer.objects.bulk_create(answers_to_create)

    return round((correct_count / total_questions) * 100, 2)


@login_required
def quiz_submit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        submission = Submission.objects.create(
            quiz=quiz,
            user=request.user,
            score=0.0
        )
        score = calculate_score(request.POST, quiz, submission)
        submission.score = score
        submission.save(update_fields=['score'])
        return redirect('quizzes:quiz_results', submission_id=submission.id)
    return redirect('quizzes:quiz_detail', pk=pk)


@login_required
def quiz_results(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    answers = submission.answers.select_related('question', 'choice')
    return render(request, 'quizzes/quiz_results.html', {
        'submission': submission,
        'answers': answers
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('quizzes:quiz_list')
    else:
        form = UserCreationForm()
    return render(request, 'quizzes/registration.html', {'form': form})


@login_required
def user_statistics(request):
    submissions = Submission.objects.filter(user=request.user).select_related('quiz')
    total_submissions = submissions.count()
    avg_score = submissions.aggregate(avg=Avg('score'))['avg'] or 0

    quiz_stats = {}
    for quiz in Quiz.objects.filter(submission__user=request.user).distinct():
        quiz_subs = submissions.filter(quiz=quiz)
        quiz_stats[quiz] = {
            'attempts': quiz_subs.count(),
            'avg_score': quiz_subs.aggregate(avg=Avg('score'))['avg'] or 0,
        }

    return render(request, 'quizzes/user_statistics.html', {
        'submissions': submissions,
        'total_submissions': total_submissions,
        'avg_score': round(avg_score, 2),
        'quiz_stats': quiz_stats,
    })