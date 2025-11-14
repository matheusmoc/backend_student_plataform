from celery import shared_task
from django.db import transaction, IntegrityError

from .models import ExamSubmission, SubmissionAnswer


@shared_task(bind=True, max_retries=3, default_retry_delay=1)
def process_exam_submission(self, payload: dict):
    """Create an ExamSubmission and its answers asynchronously.

    Payload shape:
    - student_id: int
    - exam_id: int
    - answers: list[{question_id: int, selected_option: int}]

    Returns a dict with created flag and submission info.
    """
    student_id = payload.get('student_id')
    exam_id = payload.get('exam_id')
    answers = payload.get('answers', [])

    try:
        with transaction.atomic():
            created = False
            try:
                submission, created = ExamSubmission.objects.get_or_create(
                    student_id=student_id, exam_id=exam_id
                )
            except IntegrityError:
                submission = ExamSubmission.objects.get(
                    student_id=student_id, exam_id=exam_id
                )
                created = False

            if created and answers:
                submission_answers = [
                    SubmissionAnswer(
                        submission=submission,
                        question_id=a['question_id'],
                        selected_alternative_option=a['selected_option'],
                    )
                    for a in answers
                ]
                SubmissionAnswer.objects.bulk_create(submission_answers, ignore_conflicts=True)

    except IntegrityError as exc:
        raise self.retry(exc=exc)

    return {
        'created': created,
        'submission': {
            'id': submission.id,
            'student_id': student_id,
            'exam_id': exam_id,
            'score': submission.score,
            'total_answers': submission.answers.count(),
        }
    }
