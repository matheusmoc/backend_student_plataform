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
        
        # Create a student
        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        
        # Create questions with alternatives
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
        
        # Create exam
        self.exam = Exam.objects.create(name='Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)
    
    def test_submit_exam_success(self):
        """Test successful exam submission"""
        url = '/api/exam/submit/'
        data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 2},
                {'question_id': self.question2.id, 'selected_option': 1}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] == True
        assert 'submission_id' in response.data
        assert response.data['total_answers'] == 2
        
        # Verify submission was created
        submission = ExamSubmission.objects.get(id=response.data['submission_id'])
        assert submission.student == self.student
        assert submission.exam == self.exam
        assert submission.answers.count() == 2
    
    def test_submit_exam_invalid_student(self):
        """Test submission with invalid student ID"""
        url = '/api/exam/submit/'
        data = {
            'student_id': 9999,  # Non-existent student
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
        url = '/api/exam/submit/'
        data = {
            'student_id': self.student.id,
            'exam_id': 9999,  # Non-existent exam
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
        # Create a question not in the exam
        other_question = Question.objects.create(content='Other question?')
        
        url = '/api/exam/submit/'
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
        # First submission
        ExamSubmission.objects.create(student=self.student, exam=self.exam)
        
        url = '/api/exam/submit/'
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
        url = '/api/exam/submit/'
        data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 6}  # Invalid option
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
        
        # Create student
        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        
        # Create questions with alternatives
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
        
        # Create exam
        self.exam = Exam.objects.create(name='Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)
        
        # Create submission with answers
        self.submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        
        # Create answers - 1 correct, 1 incorrect
        SubmissionAnswer.objects.create(
            submission=self.submission,
            question=self.question1,
            selected_alternative_option=2  # Correct
        )
        SubmissionAnswer.objects.create(
            submission=self.submission,
            question=self.question2,
            selected_alternative_option=2  # Incorrect
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
        """Test getting results by student ID and exam ID"""
        url = f'/api/exam/student/{self.student.id}/exam/{self.exam.id}/results/'
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        
        results = response.data['results']
        assert results['student_name'] == 'Test Student'
        assert results['exam_name'] == 'Test Exam'
        assert results['score_percentage'] == 50.0
    
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
        
        # Check first question (correct answer)
        q1 = questions[0]
        assert q1['content'] == 'Test question 1?'
        assert q1['student_answer'] == 2
        assert q1['student_answer_letter'] == 'B'
        assert q1['correct_answer'] == 2
        assert q1['correct_answer_letter'] == 'B'
        assert q1['is_correct'] == True
        assert len(q1['alternatives']) >= 2
        
        # Check second question (incorrect answer)
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
        
        # Create student
        self.student = Student.objects.create(
            username='workflowtest',
            email='workflow@example.com',
            name='Workflow Test Student'
        )
        
        # Create questions with alternatives
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
        
        # Create exam
        self.exam = Exam.objects.create(name='Workflow Test Exam')
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)
    
    def test_complete_workflow(self):
        """Test complete workflow: submit -> get results"""
        
        # Step 1: Submit exam
        submit_url = '/api/exam/submit/'
        submit_data = {
            'student_id': self.student.id,
            'exam_id': self.exam.id,
            'answers': [
                {'question_id': self.question1.id, 'selected_option': 1},  # Correct
                {'question_id': self.question2.id, 'selected_option': 2}   # Correct
            ]
        }
        
        submit_response = self.client.post(submit_url, submit_data, format='json')
        
        assert submit_response.status_code == status.HTTP_201_CREATED
        submission_id = submit_response.data['submission_id']
        
        # Step 2: Get results by submission ID
        results_url = f'/api/exam/results/{submission_id}/'
        results_response = self.client.get(results_url)
        
        assert results_response.status_code == status.HTTP_200_OK
        
        results = results_response.data['results']
        assert results['correct_answers'] == 2
        assert results['score_percentage'] == 100.0
        
        # Step 3: Get results by student/exam ID (alternative endpoint)
        alt_results_url = f'/api/exam/student/{self.student.id}/exam/{self.exam.id}/results/'
        alt_results_response = self.client.get(alt_results_url)
        
        assert alt_results_response.status_code == status.HTTP_200_OK
        assert alt_results_response.data['results']['score_percentage'] == 100.0