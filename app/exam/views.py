from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from celery.result import AsyncResult

from .models import Exam, ExamSubmission, SubmissionAnswer
from .serializers import (
    ExamSubmissionCreateSerializer,
    ExamResultSerializer,
    ExamSerializer,
    ExamDetailSerializer,
)
from .tasks import process_exam_submission

class ExamsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        search = request.query_params.get('search')
        qs = Exam.objects.all().order_by('name')
        if search:
            qs = qs.filter(name__icontains=search)
        serializer = ExamSerializer(qs, many=True)
        return Response({'success': True, 'results': serializer.data})

    def post(self, request):
        serializer = ExamSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=400)
        exam = serializer.save()
        return Response({'success': True, 'id': exam.id, 'name': exam.name}, status=201)


class ExamDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        exam = get_object_or_404(Exam.objects.prefetch_related('examquestion_set__question__alternatives'), pk=pk)
        serializer = ExamDetailSerializer(exam)
        return Response(serializer.data)

    def put(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        serializer = ExamSerializer(exam, data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=400)
        serializer.save()
        return Response({'success': True, 'result': serializer.data})

    def patch(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        serializer = ExamSerializer(exam, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=400)
        serializer.save()
        return Response({'success': True, 'result': serializer.data})

    def delete(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        exam.delete()
        return Response(status=204)


class ExamStatisticsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        submissions = ExamSubmission.objects.filter(exam=exam)
        scores = [s.score for s in submissions]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

        question_stats = []
        exam_questions = exam.examquestion_set.select_related('question').prefetch_related('question__alternatives')
        for eq in exam_questions:
            correct_alt = next((a for a in eq.question.alternatives.all() if getattr(a, 'is_correct', False)), None)
            correct_option = getattr(correct_alt, 'option', None)
            total_answers = SubmissionAnswer.objects.filter(
                question=eq.question, submission__exam=exam
            ).count()
            correct_count = SubmissionAnswer.objects.filter(
                question=eq.question, submission__exam=exam,
                selected_alternative_option=correct_option
            ).count() if correct_option is not None else 0

            question_stats.append({
                'question_id': eq.question.id,
                'question_content': getattr(eq.question, 'content', ''),
                'question_number': eq.number,
                'correct_answers': correct_count,
                'total_answers': total_answers,
                'accuracy_percentage': round((correct_count / total_answers * 100) if total_answers else 0.0, 2)
            })

        return Response({
            'success': True,
            'exam_name': exam.name,
            'statistics': {
                'total_submissions': submissions.count(),
                'average_score': avg_score,
                'questions_statistics': question_stats
            }
        })


class SubmissionsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = ExamSubmission.objects.select_related('student', 'exam').prefetch_related('answers__question__alternatives')
        student = request.query_params.get('student') or request.query_params.get('student_id')
        exam = request.query_params.get('exam') or request.query_params.get('exam_id')
        student_name = request.query_params.get('student_name')
        if student:
            qs = qs.filter(student_id=student)
        if exam:
            qs = qs.filter(exam_id=exam)
        if student_name:
            qs = qs.filter(student__name__icontains=student_name)
        qs = qs.order_by('-submitted_at')
        serializer = ExamResultSerializer(qs, many=True)
        return Response({'success': True, 'count': qs.count(), 'results': serializer.data})

class SubmissionsAsyncAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Enfileira a submissão para processamento assíncrono via Celery.

        Respostas:
        - 202 Accepted com task_id e dica de URL para acompanhar o status
        - 400 em caso de validação inválida
        """
        serializer = ExamSubmissionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        payload = serializer.validated_data
        task = process_exam_submission.delay(payload)
        return Response({
            'success': True,
            'message': 'Submissão recebida e enfileirada',
            'processing': 'asynchronous',
            'task_id': task.id,
            'poll_url_hint': f"/api/exam/submissions/status/?task_id={task.id}",
        }, status=status.HTTP_202_ACCEPTED)


class SubmissionStatusAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'success': False, 'error': 'task_id é obrigatório'}, status=400)
        res = AsyncResult(task_id)
        data = {'state': res.state}
        if res.successful():
            result = res.result or {}
            data.update({'created': result.get('created'), 'submission': result.get('submission')})
            return Response({'success': True, 'task': data})
        if res.failed():
            data.update({'error': str(res.result)})
            return Response({'success': True, 'task': data}, status=500)
        return Response({'success': True, 'task': data}, status=202)


class SubmissionDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        submission = get_object_or_404(
            ExamSubmission.objects.select_related('student', 'exam').prefetch_related('answers__question__alternatives'),
            pk=pk
        )
        serializer = ExamResultSerializer(submission)
        return Response({'success': True, 'results': serializer.data})


class StudentSubmissionsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({'success': False, 'error': 'Parameter student_id is required'}, status=400)
        qs = ExamSubmission.objects.select_related('student', 'exam').prefetch_related('answers__question__alternatives').filter(student_id=student_id)
        serializer = ExamResultSerializer(qs, many=True)
        avg = round(sum(s.score for s in qs) / qs.count(), 2) if qs.exists() else 0.0
        return Response({
            'success': True,
            'student_id': str(student_id),
            'total_submissions': qs.count(),
            'average_score': avg,
            'submissions': serializer.data
        })


class StudentExamResultsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, student_id, exam_id):
        try:
            submission = ExamSubmission.objects.select_related('student', 'exam').prefetch_related('answers__question__alternatives').get(
                student_id=student_id, exam_id=exam_id
            )
        except ExamSubmission.DoesNotExist:
            return Response({'success': False, 'error': 'Submissão não encontrada para este estudante e exame'}, status=404)
        serializer = ExamResultSerializer(submission)
        return Response({'success': True, 'results': serializer.data})


class SubmissionDetailedAnalysisAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        submission = get_object_or_404(
            ExamSubmission.objects.select_related('student', 'exam'),
            pk=pk
        )
        exam = submission.exam
        other_submissions = ExamSubmission.objects.filter(exam=exam).exclude(id=submission.id)
        if other_submissions.exists():
            avg_score = other_submissions.aggregate(avg=Avg('score'))['avg']
            better_than = other_submissions.filter(score__lt=submission.score).count()
            total_others = other_submissions.count()
            percentile = round((better_than / total_others * 100) if total_others > 0 else 0, 2)
        else:
            avg_score = submission.score
            percentile = 100
        return Response({
            'success': True,
            'submission': ExamResultSerializer(submission).data,
            'comparison': {
                'exam_average_score': round(avg_score or 0, 2),
                'your_score': submission.score,
                'percentile': percentile,
                'total_submissions': other_submissions.count() + 1
            }
        })
