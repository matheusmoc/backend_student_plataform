"""
Filtros customizados para a aplicação de exames
"""
import django_filters
from django.db.models import Q
from .models import Exam, ExamSubmission


class ExamFilter(django_filters.FilterSet):
    """Filtros para o modelo Exam"""
    
    name = django_filters.CharFilter(lookup_expr='icontains', help_text='Filtrar por nome (parcial)')
    has_questions = django_filters.BooleanFilter(
        method='filter_has_questions', 
        help_text='Filtrar exames que têm ou não têm questões'
    )
    min_questions = django_filters.NumberFilter(
        method='filter_min_questions',
        help_text='Filtrar exames com número mínimo de questões'
    )
    
    class Meta:
        model = Exam
        fields = ['name', 'has_questions', 'min_questions']
    
    def filter_has_questions(self, queryset, name, value):
        """Filtra exames que têm ou não têm questões"""
        if value:
            return queryset.filter(examquestion__isnull=False).distinct()
        return queryset.filter(examquestion__isnull=True).distinct()
    
    def filter_min_questions(self, queryset, name, value):
        """Filtra exames com número mínimo de questões"""
        if value is not None:
            return queryset.annotate(
                question_count=django_filters.Count('examquestion')
            ).filter(question_count__gte=value)
        return queryset


class ExamSubmissionFilter(django_filters.FilterSet):
    """Filtros para o modelo ExamSubmission"""
    
    student_name = django_filters.CharFilter(
        field_name='student__name', 
        lookup_expr='icontains',
        help_text='Filtrar por nome do estudante (parcial)'
    )
    exam_name = django_filters.CharFilter(
        field_name='exam__name',
        lookup_expr='icontains', 
        help_text='Filtrar por nome do exame (parcial)'
    )
    min_score = django_filters.NumberFilter(
        method='filter_min_score',
        help_text='Filtrar submissões com pontuação mínima'
    )
    max_score = django_filters.NumberFilter(
        method='filter_max_score',
        help_text='Filtrar submissões com pontuação máxima'
    )
    submitted_date = django_filters.DateFromToRangeFilter(
        field_name='submitted_at__date',
        help_text='Filtrar por intervalo de datas de submissão'
    )
    
    class Meta:
        model = ExamSubmission
        fields = [
            'student', 'exam', 'student_name', 'exam_name', 
            'min_score', 'max_score', 'submitted_date'
        ]
    
    def filter_min_score(self, queryset, name, value):
        """Filtra submissões com pontuação mínima"""
        if value is not None:
            filtered_ids = []
            for submission in queryset:
                if submission.score >= value:
                    filtered_ids.append(submission.id)
            return queryset.filter(id__in=filtered_ids)
        return queryset
    
    def filter_max_score(self, queryset, name, value):
        """Filtra submissões com pontuação máxima"""
        if value is not None:
            filtered_ids = []
            for submission in queryset:
                if submission.score <= value:
                    filtered_ids.append(submission.id)
            return queryset.filter(id__in=filtered_ids)
        return queryset