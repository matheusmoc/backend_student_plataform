from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from .models import Exam, ExamSubmission, SubmissionAnswer
from .serializers import (
    ExamSubmissionCreateSerializer, 
    ExamResultSerializer,
    ExamSerializer,
    ExamDetailSerializer
)
from .filters import ExamFilter, ExamSubmissionFilter


class ExamViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para operações CRUD de Exames
    
    Endpoints disponíveis:
    - GET /api/exam/exams/ - Listar todos os exames
    - POST /api/exam/exams/ - Criar novo exame
    - GET /api/exam/exams/{id}/ - Obter exame específico
    - PUT /api/exam/exams/{id}/ - Atualizar exame completo
    - PATCH /api/exam/exams/{id}/ - Atualizar exame parcialmente
    - DELETE /api/exam/exams/{id}/ - Deletar exame
    - GET /api/exam/exams/{id}/statistics/ - Estatísticas do exame
    """
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ExamFilter
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Retorna serializer diferente baseado na action"""
        if self.action == 'retrieve':
            return ExamDetailSerializer
        return ExamSerializer
    
    def get_queryset(self):
        """Otimiza queryset com prefetch para melhor performance"""
        queryset = super().get_queryset()
        
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'examquestion_set__question__alternatives'
            ).select_related()
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Endpoint para obter estatísticas do exame
        GET /api/exam/{id}/statistics/
        """
        exam = self.get_object()
        stats = ExamSubmission.objects.filter(exam=exam).aggregate(
            total_submissions=Count('id'),
            average_score=Avg('score')
        )
        
        question_stats = []
        for exam_question in exam.examquestion_set.all():
            correct_count = SubmissionAnswer.objects.filter(
                question=exam_question.question,
                submission__exam=exam
            ).filter(
                selected_alternative_option=exam_question.question.alternatives.filter(
                    is_correct=True
                ).first().option
            ).count()
            
            total_answers = SubmissionAnswer.objects.filter(
                question=exam_question.question,
                submission__exam=exam
            ).count()
            
            question_stats.append({
                'question_id': exam_question.question.id,
                'question_content': exam_question.question.content,
                'question_number': exam_question.number,
                'correct_answers': correct_count,
                'total_answers': total_answers,
                'accuracy_percentage': round(
                    (correct_count / total_answers * 100) if total_answers > 0 else 0, 2
                )
            })
        
        return Response({
            'success': True,
            'exam_name': exam.name,
            'statistics': {
                'total_submissions': stats['total_submissions'] or 0,
                'average_score': round(stats['average_score'] or 0, 2),
                'questions_statistics': question_stats
            }
        })


class ExamSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Submissões de Exames
    
    Endpoints disponíveis:
    - GET /api/exam/submissions/ - Listar submissões
    - POST /api/exam/submissions/ - Criar nova submissão
    - GET /api/exam/submissions/{id}/ - Obter submissão específica
    - PUT /api/exam/submissions/{id}/ - Atualizar submissão
    - DELETE /api/exam/submissions/{id}/ - Deletar submissão
    - GET /api/exam/submissions/my_submissions/ - Submissões do usuário
    - GET /api/exam/submissions/{id}/detailed_analysis/ - Análise detalhada
    """
    queryset = ExamSubmission.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ExamSubmissionFilter
    search_fields = ['student__name', 'exam__name']
    ordering_fields = ['submitted_at', 'student__name', 'exam__name']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        """Otimiza queryset com select_related e prefetch_related"""
        return ExamSubmission.objects.select_related(
            'student', 'exam'
        ).prefetch_related(
            'answers__question__alternatives'
        )
    
    def get_serializer_class(self):
        """Usa serializers diferentes para cada action"""
        if self.action == 'create':
            return ExamSubmissionCreateSerializer
        return ExamResultSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Submete respostas de exame
        POST /api/submissions/
        
        Expected payload:
        {
            "student_id": 1,
            "exam_id": 1,
            "answers": [
                {"question_id": 1, "selected_option": 3},
                {"question_id": 2, "selected_option": 2}
            ]
        }
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            submission = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Exame submetido com sucesso',
                'submission_id': submission.id,
                'submitted_at': submission.submitted_at,
                'total_answers': submission.answers.count(),
                'score': submission.score
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obter resultados detalhados de uma submissão
        GET /api/submissions/{id}/
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'results': serializer.data
        })
    
    def list(self, request, *args, **kwargs):
        """
        Listar submissões com filtros opcionais
        GET /api/submissions/
        
        Query params:
        - student: ID do estudante
        - exam: ID do exame  
        - student__name: Nome do estudante
        - ordering: Campo para ordenação
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginação
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """
        Endpoint para estudante ver suas próprias submissões
        GET /api/submissions/my_submissions/?student_id={id}
        """
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response({
                'success': False,
                'error': 'Parameter student_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(student_id=student_id)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'student_id': student_id,
            'total_submissions': queryset.count(),
            'average_score': queryset.aggregate(avg=Avg('score'))['avg'] or 0,
            'submissions': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='student/<int:student_id>/exam/<int:exam_id>')
    def student_exam_results(self, request, student_id=None, exam_id=None):
        """
        Endpoint alternativo para obter resultados por student_id e exam_id
        GET /api/submissions/student/{student_id}/exam/{exam_id}/
        """
        try:
            submission = self.get_queryset().get(
                student_id=student_id,
                exam_id=exam_id
            )
        except ExamSubmission.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Submissão não encontrada para este estudante e exame'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(submission)
        
        return Response({
            'success': True,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def detailed_analysis(self, request, pk=None):
        """
        Análise detalhada da submissão com comparações
        GET /api/submissions/{id}/detailed_analysis/
        """
        submission = self.get_object()
        exam = submission.exam
        
        # Comparar com outras submissões do mesmo exame
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
