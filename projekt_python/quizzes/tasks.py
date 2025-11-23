import dramatiq
from django.db import transaction
from .models import Submission, Question


@dramatiq.actor
def grade_submission(submission_id: int) -> None:
    with transaction.atomic():

        submission = (
            Submission.objects
            .select_for_update()
            .select_related('quiz')
            .get(id=submission_id)
        )


        answers = submission.answers.select_related('choice', 'question').all()
        answered_question_ids = {a.question_id for a in answers}

        total_questions = Question.objects.filter(quiz=submission.quiz).count()

        if total_questions == 0:
            final_score = 0.0
        else:

            correct_count = sum(1 for a in answers if a.choice.is_correct)

            final_score = round((correct_count / total_questions) * 100, 2)


        submission.score = final_score
        submission.save(update_fields=["score"])