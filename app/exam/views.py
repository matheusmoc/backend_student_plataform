from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ExamSubmission
from .serializers import ExamSubmissionCreateSerializer, ExamResultSerializer


@api_view(['POST'])
def submit_exam(request):
    """
    Expected payload:
    {
        "student_id": 1,
        "exam_id": 1,
        "answers": [
            {"question_id": 1, "selected_option": 3},
            {"question_id": 2, "selected_option": 2},
        ]
    }
    """
    serializer = ExamSubmissionCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        submission = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Exam submitted successfully',
            'submission_id': submission.id,
            'submitted_at': submission.submitted_at,
            'total_answers': submission.answers.count()
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def exam_results(request, submission_id):
    """
    API endpoint to get detailed exam results showing correct/incorrect answers
    and overall score percentage
    
    URL: /api/exam-results/<submission_id>/
    """
    submission = get_object_or_404(
        ExamSubmission.objects.select_related('student', 'exam')
                              .prefetch_related('answers__question__alternatives'),
        id=submission_id
    )
    
    serializer = ExamResultSerializer(submission)
    
    return Response({
        'success': True,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def student_exam_results(request, student_id, exam_id):
    """
    Alternative endpoint to get exam results by student and exam IDs
    
    URL: /api/student/<student_id>/exam/<exam_id>/results/
    """
    submission = get_object_or_404(
        ExamSubmission.objects.select_related('student', 'exam')
                              .prefetch_related('answers__question__alternatives'),
        student_id=student_id,
        exam_id=exam_id
    )
    
    serializer = ExamResultSerializer(submission)
    
    return Response({
        'success': True,
        'results': serializer.data
    }, status=status.HTTP_200_OK)
