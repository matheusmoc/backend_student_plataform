"""
Pytest tests for exam submission functionality
Run with: pytest test_exam_functionality.py -v
"""

import pytest
from django.test import TestCase
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
import json

# Import models
from exam.models import Exam, ExamQuestion, ExamSubmission, SubmissionAnswer
from question.models import Question, Alternative
from student.models import Student
from exam.serializers import ExamSubmissionCreateSerializer, ExamResultSerializer


class TestImports:
    """Test that all necessary imports work"""
    
    def test_model_imports(self):
        """Test model imports"""
        from exam.models import Exam, ExamQuestion, ExamSubmission, SubmissionAnswer
        from question.models import Question, Alternative
        from student.models import Student
        
        assert Exam is not None
        assert ExamQuestion is not None
        assert ExamSubmission is not None
        assert SubmissionAnswer is not None
        assert Question is not None
        assert Alternative is not None
        assert Student is not None
    
    def test_serializer_imports(self):
        """Test serializer imports"""
        from exam.serializers import ExamSubmissionCreateSerializer, ExamResultSerializer
        
        assert ExamSubmissionCreateSerializer is not None
        assert ExamResultSerializer is not None
    
    def test_view_imports(self):
        """Test view imports"""
        from exam.views import submit_exam, exam_results, student_exam_results
        
        assert submit_exam is not None
        assert exam_results is not None
        assert student_exam_results is not None


class TestModelStructure:
    """Test model structure and relationships"""
    
    def test_exam_submission_fields(self):
        """Test ExamSubmission model fields"""
        submission_fields = [field.name for field in ExamSubmission._meta.get_fields()]
        expected_fields = ['id', 'student', 'exam', 'submitted_at', 'answers']
        
        for field in expected_fields:
            assert field in submission_fields, f"ExamSubmission missing {field} field"
    
    def test_submission_answer_fields(self):
        """Test SubmissionAnswer model fields"""
        answer_fields = [field.name for field in SubmissionAnswer._meta.get_fields()]
        expected_fields = ['id', 'submission', 'question', 'selected_alternative_option']
        
        for field in expected_fields:
            assert field in answer_fields, f"SubmissionAnswer missing {field} field"
    
    def test_model_constraints(self):
        """Test model unique constraints"""
        submission_meta = ExamSubmission._meta
        answer_meta = SubmissionAnswer._meta
        
        assert ('student', 'exam') in submission_meta.unique_together
        assert ('submission', 'question') in answer_meta.unique_together
    
    def test_model_properties(self):
        """Test model properties exist"""
        # Test that properties exist (without calling them to avoid DB errors)
        assert hasattr(ExamSubmission, 'score')
        assert hasattr(ExamSubmission, 'correct_answers_count')
        assert hasattr(SubmissionAnswer, 'is_correct')


class TestSerializerStructure:
    """Test serializer basic structure"""
    
    def test_exam_submission_create_serializer_fields(self):
        """Test ExamSubmissionCreateSerializer has required fields"""
        serializer = ExamSubmissionCreateSerializer()
        fields = list(serializer.fields.keys())
        expected_fields = ['student_id', 'exam_id', 'answers']
        
        for field in expected_fields:
            assert field in fields, f"ExamSubmissionCreateSerializer missing {field} field"
    
    def test_exam_result_serializer_fields(self):
        """Test ExamResultSerializer has required fields"""
        serializer = ExamResultSerializer()
        fields = list(serializer.fields.keys())
        expected_fields = ['id', 'student_name', 'exam_name', 'submitted_at', 
                          'total_questions', 'correct_answers', 'score_percentage', 'questions']
        
        for field in expected_fields:
            assert field in fields, f"ExamResultSerializer missing {field} field"


class TestURLConfiguration:
    """Test URL configuration"""
    
    def test_exam_urls_exist(self):
        """Test that exam.urls module exists and has patterns"""
        import exam.urls
        
        assert hasattr(exam.urls, 'urlpatterns')
        assert len(exam.urls.urlpatterns) >= 3
    
    def test_url_patterns(self):
        """Test specific URL patterns"""
        import exam.urls
        
        pattern_names = [pattern.name for pattern in exam.urls.urlpatterns if hasattr(pattern, 'name')]
        expected_patterns = ['submit_exam', 'exam_results', 'student_exam_results']
        
        for pattern in expected_patterns:
            assert pattern in pattern_names, f"Missing URL pattern: {pattern}"


@pytest.mark.django_db
class TestModelFunctionality(TestCase):
    """Test model functionality with database"""
    
    def setUp(self):
        """Set up test data"""
        # Create a student
        self.student = Student.objects.create(
            username='teststudent',
            email='test@example.com',
            name='Test Student'
        )
        
        # Create questions
        self.question1 = Question.objects.create(content='Test question 1?')
        self.question2 = Question.objects.create(content='Test question 2?')
        
        # Create alternatives
        Alternative.objects.create(
            question=self.question1, content='Option A', option=1, is_correct=False
        )
        Alternative.objects.create(
            question=self.question1, content='Option B', option=2, is_correct=True
        )
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
    
    def test_exam_submission_creation(self):
        """Test creating an ExamSubmission"""
        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        
        assert submission.id is not None
        assert submission.student == self.student
        assert submission.exam == self.exam
        assert submission.submitted_at is not None
    
    def test_submission_answer_creation(self):
        """Test creating SubmissionAnswers"""
        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        
        answer = SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question1,
            selected_alternative_option=2
        )
        
        assert answer.id is not None
        assert answer.submission == submission
        assert answer.question == self.question1
        assert answer.selected_alternative_option == 2
        assert answer.is_correct == True  # Option 2 is correct for question1
    
    def test_submission_score_calculation(self):
        """Test score calculation"""
        submission = ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        
        # Create answers - 1 correct, 1 incorrect
        SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question1,
            selected_alternative_option=2  # Correct
        )
        SubmissionAnswer.objects.create(
            submission=submission,
            question=self.question2,
            selected_alternative_option=2  # Incorrect (correct is 1)
        )
        
        assert submission.score == 50.0  # 1 out of 2 correct = 50%
        assert submission.correct_answers_count == 1
    
    def test_unique_constraint_student_exam(self):
        """Test that student can only submit exam once"""
        ExamSubmission.objects.create(
            student=self.student,
            exam=self.exam
        )
        
        with pytest.raises(IntegrityError):
            ExamSubmission.objects.create(
                student=self.student,
                exam=self.exam
            )


class TestSerializerValidation:
    """Test serializer validation logic"""
    
    def test_answer_submission_serializer(self):
        """Test AnswerSubmissionSerializer validation"""
        from exam.serializers import AnswerSubmissionSerializer
        
        # Valid data
        valid_data = {'question_id': 1, 'selected_option': 3}
        serializer = AnswerSubmissionSerializer(data=valid_data)
        assert serializer.is_valid()
        
        # Invalid option (too high)
        invalid_data = {'question_id': 1, 'selected_option': 6}
        serializer = AnswerSubmissionSerializer(data=invalid_data)
        assert not serializer.is_valid()
        
        # Invalid option (too low)
        invalid_data = {'question_id': 1, 'selected_option': 0}
        serializer = AnswerSubmissionSerializer(data=invalid_data)
        assert not serializer.is_valid()


# Test runner function for backwards compatibility
def run_pytest_tests():
    """Run all pytest tests"""
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'test_exam_functionality.py', 
        '-v', '--tb=short'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    print("Running pytest tests...")
    print("Use 'pytest test_exam_functionality.py -v' for better output")
    run_pytest_tests()