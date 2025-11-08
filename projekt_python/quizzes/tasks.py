import dramatiq
from django.db import transaction

from .models import Submission


@dramatiq.actor
def grade_submission(submission_id: int) -> None:
    with transaction.atomic():
        submission = Submission.objects.select_for_update().get(id=submission_id)
        answers = submission.answers.select_related("choice").all()
        score = sum(1 for a in answers if a.choice.is_correct)
        submission.score = score
        submission.save(update_fields=["score"])




