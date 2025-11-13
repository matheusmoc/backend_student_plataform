"""
Testes para as ViewSets de Exam usando DRF e pytest
"""

import pytest
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from exam.models import Exam, ExamQuestion, ExamSubmission, SubmissionAnswer
from question.models import Question, Alternative
from student.models import Student


User = get_user_model()


@pytest.mark.django_db
class TestExamViewSet(APITestCase):
    """Testes para ExamViewSet"""
    
    def setUp(self):
        """Setup para os testes"""
        self.client = APIClient()
        
        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        
        self.question1 = Question.objects.create(content='Test question 1?')
        Alternative.objects.create(
            question=self.question1, content='Option A', option=1, is_correct=True
        )
        Alternative.objects.create(
            question=self.question1, content='Option B', option=2, is_correct=False
        )

        self.exam = Exam.objects.create(name='Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
    
    def test_list_exams(self):
        """Teste listar todos os exames"""
        url = '/api/exam/exams/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Test Exam'
    
    def test_retrieve_exam(self):
        """Teste obter exame específico"""
        url = f'/api/exam/exams/{self.exam.id}/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Exam'
        assert response.data['total_questions'] == 1
        assert len(response.data['questions']) == 1
    
    def test_search_exams(self):
        """Teste busca por nome de exame"""
        url = '/api/exam/exams/?search=Test'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        
        # Busca que não deve retornar resultados
        url = '/api/exam/exams/?search=NonExistent'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_exam_statistics(self):
        """Teste endpoint de estatísticas do exame"""
        # Criar uma submissão para gerar estatísticas
        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question1,
            selected_alternative_option=1  # Resposta correta
        )
        
        url = f'/api/exam/exams/{self.exam.id}/statistics/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        assert response.data['exam_name'] == 'Test Exam'
        assert response.data['statistics']['total_submissions'] == 1
        assert len(response.data['statistics']['questions_statistics']) == 1


@pytest.mark.django_db
class TestExamSubmissionViewSet(APITestCase):
    """Testes para ExamSubmissionViewSet"""
    
    def setUp(self):
        """Setup para os testes"""
        self.client = APIClient()
        
        # Criar usuário/estudante
        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        

        self.question1 = Question.objects.create(content='Test question 1?')
        Alternative.objects.create(
            question=self.question1, content='Option A', option=1, is_correct=True
        )
        Alternative.objects.create(
            question=self.question1, content='Option B', option=2, is_correct=False
        )
        
        self.question2 = Question.objects.create(content='Test question 2?')
        Alternative.objects.create(
            question=self.question2, content='Option A', option=1, is_correct=False
        )
        Alternative.objects.create(
            question=self.question2, content='Option B', option=2, is_correct=True
        )
        
        # Criar exame
        self.exam = Exam.objects.create(name='Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)
    
    def test_create_submission(self):
        """Teste criar nova submissão"""
        url = '/api/exam/submissions/'
        data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 1},
                {'question_id': self.question2.id, 'selected_option': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] == True
        assert 'submission_id' in response.data
        assert response.data['score'] == 100.0  # Ambas corretas
    
    def test_list_submissions(self):
        """Teste listar submissões"""
  
        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question1,
            selected_alternative_option=1
        )
        
        url = '/api/exam/submissions/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        assert response.data['count'] == 1
    
    def test_retrieve_submission(self):
        """Teste obter submissão específica"""

        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question1,
            selected_alternative_option=1
        )
        
        url = f'/api/exam/submissions/{submission.id}/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        assert response.data['results']['student_name'] == 'Test Student'
    
    def test_my_submissions(self):
        """Teste endpoint de minhas submissões"""

        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        
        url = f'/api/exam/submissions/my_submissions/?student_id={self.student.id}'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        assert response.data['total_submissions'] == 1
        assert response.data['student_id'] == str(self.student.id)
    
    def test_detailed_analysis(self):
        """Teste análise detalhada da submissão"""

        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question1,
            selected_alternative_option=1  # Correta
        )
        SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question2,
            selected_alternative_option=1  # Incorreta
        )
        
        url = f'/api/exam/submissions/{submission.id}/detailed_analysis/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        assert 'submission' in response.data
        assert 'comparison' in response.data
        assert response.data['comparison']['your_score'] == 50.0
    
    def test_filter_submissions_by_student_name(self):
        """Teste filtrar submissões por nome do estudante"""

        ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        
        url = '/api/exam/submissions/?student_name=Test'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        
        url = '/api/exam/submissions/?student_name=NonExistent'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0


@pytest.mark.django_db
class TestExamViewSetPermissions(APITestCase):
    """Testes de permissões para ViewSets"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        
        self.exam = Exam.objects.create(name='Test Exam')
    
    def test_anonymous_can_read_exams(self):
        """Teste que usuários anônimos podem ler exames"""
        url = '/api/exam/exams/'
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_anonymous_cannot_create_exam(self):
        """Teste que usuários anônimos não podem criar exames"""
        url = '/api/exam/exams/'
        data = {'name': 'New Exam'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]