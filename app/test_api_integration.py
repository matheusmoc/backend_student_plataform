"""
API Integration tests for exam submission functionality
Run with: pytest test_api_integration.py -v
"""

import pytest
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
import json

from exam.models import Exam, ExamQuestion, ExamSubmission, SubmissionAnswer
from question.models import Question, Alternative
from student.models import Student


@pytest.mark.django_db
class TestExamSubmissionAPI(APITestCase):
    """Test exam submission API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        
        self.question1 = Question.objects.create(content='Test question 1?')
        Alternative.objects.create(
            question=self.question1, content='Option A', option=1, is_correct=False
        )
        Alternative.objects.create(
            question=self.question1, content='Option B', option=2, is_correct=True
        )
        Alternative.objects.create(
            question=self.question1, content='Option C', option=3, is_correct=False
        )
        
        self.question2 = Question.objects.create(content='Test question 2?')
        Alternative.objects.create(
            question=self.question2, content='Option A', option=1, is_correct=True
        )
        Alternative.objects.create(
            question=self.question2, content='Option B', option=2, is_correct=False
        )
        
        self.exam = Exam.objects.create(name='Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)
    
    def test_submit_exam_success(self):
        """Test successful exam submission using async endpoint"""
        url = '/api/exam/submissions/'
        data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 2},
                {'question_id': self.question2.id, 'selected_option': 1}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data['success'] == True
        assert 'task_id' in response.data


        status_url = f"/api/exam/submissions/status/?task_id={response.data['task_id']}"
        status_resp = self.client.get(status_url)
        assert status_resp.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        assert status_resp.data['success'] == True
    
        if status_resp.status_code == status.HTTP_200_OK:
            submission_id = status_resp.data['task']['submission']['id']
        else:
          
            status_resp = self.client.get(status_url)
            assert status_resp.status_code == status.HTTP_200_OK
            submission_id = status_resp.data['task']['submission']['id']

        submission = ExamSubmission.objects.get(id=submission_id)
        assert submission.student == self.student
        assert submission.exam == self.exam
        assert submission.answers.count() == 2
    
    def test_submit_exam_invalid_student(self):
        """Test submission with invalid student ID"""
        url = '/api/exam/submissions/'
        data = {
            'student_id': 9999,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] == False
        assert 'student_id' in response.data['errors']
    
    def test_submit_exam_invalid_exam(self):
        """Test submission with invalid exam ID"""
        url = '/api/exam/submissions/'
        data = {
            'student_id': self.student.id,
            'exam_id': 9999,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] == False
        assert 'exam_id' in response.data['errors']
    
    def test_submit_exam_invalid_question(self):
        """Test submission with question not belonging to exam"""

        other_question = Question.objects.create(content='Other question?')
        
        url = '/api/exam/submissions/'
        data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': other_question.id, 'selected_option': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] == False
        assert 'non_field_errors' in response.data['errors']
    
    def test_submit_exam_duplicate_submission(self):
        """Test that duplicate submissions are prevented"""

        ExamSubmission.objects.create(student=self.student, exam=self.exam)
        
        url = '/api/exam/submissions/'
        data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] == False
        assert 'non_field_errors' in response.data['errors']
    
    def test_submit_exam_invalid_option(self):
        """Test submission with invalid option number"""
        url = '/api/exam/submissions/'
        data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 6} 
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] == False


@pytest.mark.django_db
class TestExamResultsAPI(APITestCase):
    """Test exam results API endpoints"""
    
    def setUp(self):
        """Set up test data with a complete submission"""
        self.client = APIClient()
        

        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        
        self.question1 = Question.objects.create(content='Test question 1?')
        Alternative.objects.create(
            question=self.question1, content='Option A', option=1, is_correct=False
        )
        Alternative.objects.create(
            question=self.question1, content='Option B', option=2, is_correct=True
        )
        
        self.question2 = Question.objects.create(content='Test question 2?')
        Alternative.objects.create(
            question=self.question2, content='Option A', option=1, is_correct=True
        )
        Alternative.objects.create(
            question=self.question2, content='Option B', option=2, is_correct=False
        )
        

        self.exam = Exam.objects.create(name='Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)
        

        self.submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        

        SubmissionAnswer.objects.create(
            submission=self.submission,
            question=self.question1,
            selected_alternative_option=2 
        )
        SubmissionAnswer.objects.create(
            submission=self.submission,
            question=self.question2,
            selected_alternative_option=2 
        )
    
    def test_get_exam_results_by_submission_id(self):
        """Test getting results by submission ID"""
        url = f'/api/exam/results/{self.submission.id}/'
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        
        results = response.data['results']
        assert results['id'] == self.submission.id
        assert results['student_name'] == 'Test Student'
        assert results['exam_name'] == 'Test Exam'
        assert results['total_questions'] == 2
        assert results['correct_answers'] == 1
        assert results['score_percentage'] == 50.0
        assert len(results['questions']) == 2
    
    def test_get_exam_results_by_student_and_exam(self):
        """Test getting results by student ID and exam ID via ViewSet"""
      
        url = f'/api/exam/submissions/?student_id={self.student.id}&exam_id={self.exam.id}'

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

        assert isinstance(response.data, list) or 'results' in response.data
        
       
        submissions_data = response.data
        if isinstance(submissions_data, dict) and 'results' in submissions_data:
            submissions_data = submissions_data['results']
        
        assert isinstance(submissions_data, list) 
    
    def test_get_exam_results_not_found(self):
        """Test 404 for non-existent submission"""
        url = '/api/exam/results/9999/'
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_exam_results_question_details(self):
        """Test detailed question information in results"""
        url = f'/api/exam/results/{self.submission.id}/'
        
        response = self.client.get(url)
        
        questions = response.data['results']['questions']
        
        q1 = questions[0]
        assert q1['content'] == 'Test question 1?'
        assert q1['student_answer'] == 2
        assert q1['student_answer_letter'] == 'B'
        assert q1['correct_answer'] == 2
        assert q1['correct_answer_letter'] == 'B'
        assert q1['is_correct'] == True
        assert len(q1['alternatives']) >= 2
        
        q2 = questions[1]
        assert q2['content'] == 'Test question 2?'
        assert q2['student_answer'] == 2
        assert q2['student_answer_letter'] == 'B'
        assert q2['correct_answer'] == 1
        assert q2['correct_answer_letter'] == 'A'
        assert q2['is_correct'] == False


@pytest.mark.django_db
class TestCompleteWorkflow(APITestCase):
    """Test complete workflow from submission to results"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.student = Student.objects.create(
            username='workflowtest',
            email='workflow@example.com',
            name='Workflow Test Student'
        )
        
        self.question1 = Question.objects.create(content='Workflow question 1?')
        Alternative.objects.create(
            question=self.question1, content='Option A', option=1, is_correct=True
        )
        Alternative.objects.create(
            question=self.question1, content='Option B', option=2, is_correct=False
        )
        
        self.question2 = Question.objects.create(content='Workflow question 2?')
        Alternative.objects.create(
            question=self.question2, content='Option A', option=1, is_correct=False
        )
        Alternative.objects.create(
            question=self.question2, content='Option B', option=2, is_correct=True
        )
        
        self.exam = Exam.objects.create(name='Workflow Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)
    
    def test_complete_workflow(self):
        """Test complete workflow: submit -> get results"""
        
        submit_url = '/api/exam/submissions/'
        submit_data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 1}, 
                {'question_id': self.question2.id, 'selected_option': 2}  
            ]
        }
        
        submit_response = self.client.post(submit_url, submit_data, format='json')
        
        assert submit_response.status_code == status.HTTP_202_ACCEPTED
        task_id = submit_response.data['task_id']
       
        status_url = f"/api/exam/submissions/status/?task_id={task_id}"
        status_resp = self.client.get(status_url)
        assert status_resp.status_code == status.HTTP_200_OK
        submission_id = status_resp.data['task']['submission']['id']
        
        results_url = f'/api/exam/results/{submission_id}/'
        results_response = self.client.get(results_url)
        
        assert results_response.status_code == status.HTTP_200_OK
        
        results = results_response.data['results']
        assert results['correct_answers'] == 2
        assert results['score_percentage'] == 100.0
        

        alt_results_url = f'/api/exam/submissions/?student_id={self.student.id}&exam_id={self.exam.id}'
        alt_results_response = self.client.get(alt_results_url)

        assert alt_results_response.status_code == status.HTTP_200_OK

        submissions_data = alt_results_response.data
        if isinstance(submissions_data, dict) and 'results' in submissions_data:
            submissions_data = submissions_data['results']
        
        assert len(submissions_data) > 0 