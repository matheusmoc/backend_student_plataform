from rest_framework import serializers
from django.db import transaction
from .models import Exam, ExamSubmission, SubmissionAnswer, ExamQuestion
from question.models import Question, Alternative
from student.models import Student


class QuestionSimpleSerializer(serializers.ModelSerializer):
    """Serializer simples para questões em listagens"""
    
    class Meta:
        model = Question
        fields = ['id', 'content']


class ExamQuestionSerializer(serializers.ModelSerializer):
    """Serializer para relação Exam-Question"""
    question = QuestionSimpleSerializer(read_only=True)
    
    class Meta:
        model = ExamQuestion
        fields = ['number', 'question']


class ExamSerializer(serializers.ModelSerializer):
    """Serializer básico para Exam"""
    total_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ['id', 'name', 'total_questions']
    
    def get_total_questions(self, obj):
        """Conta o total de questões do exame"""
        return obj.examquestion_set.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para Exam com questões"""
    questions = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    total_submissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ['id', 'name', 'questions', 'total_questions', 'total_submissions']
    
    def get_questions(self, obj):
        """Retorna questões ordenadas por número"""
        exam_questions = obj.examquestion_set.select_related('question').order_by('number')
        return ExamQuestionSerializer(exam_questions, many=True).data
    
    def get_total_questions(self, obj):
        """Conta o total de questões do exame"""
        return obj.examquestion_set.count()
    
    def get_total_submissions(self, obj):
        """Conta o total de submissões do exame"""
        return obj.examsubmission_set.count()


class AnswerSubmissionSerializer(serializers.Serializer):
    """Serializer for individual answer submission"""
    question_id = serializers.IntegerField()
    selected_option = serializers.IntegerField(min_value=1, max_value=5)  # A-E (1-5)


class ExamSubmissionCreateSerializer(serializers.Serializer):
    """Serializer for creating an exam submission with all answers"""
    student_id = serializers.IntegerField()
    exam_id = serializers.IntegerField()
    answers = AnswerSubmissionSerializer(many=True)

    def validate_student_id(self, value):
        """Validate that student exists"""
        try:
            Student.objects.get(id=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student does not exist")
        return value

    def validate_exam_id(self, value):
        """Validate that exam exists"""
        try:
            Exam.objects.get(id=value)
        except Exam.DoesNotExist:
            raise serializers.ValidationError("Exam does not exist")
        return value

    def validate_answers(self, value):
        """Validate that all questions exist and belong to the exam"""
        if not value:
            raise serializers.ValidationError("At least one answer is required")
        
        question_ids = [answer['question_id'] for answer in value]
        
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("Duplicate questions found in answers")
        
        existing_questions = Question.objects.filter(id__in=question_ids)
        if existing_questions.count() != len(question_ids):
            raise serializers.ValidationError("One or more questions do not exist")
        
        return value

    def validate(self, data):
        """Cross-field validation to ensure questions belong to the exam"""
        exam_id = data['exam_id']
        student_id = data['student_id']
        answers = data['answers']
        
        exam = Exam.objects.get(id=exam_id)
        
        exam_question_ids = set(exam.questions.values_list('id', flat=True))
        submitted_question_ids = set(answer['question_id'] for answer in answers)
        
        if not submitted_question_ids.issubset(exam_question_ids):
            invalid_questions = submitted_question_ids - exam_question_ids
            raise serializers.ValidationError(
                f"Questions {list(invalid_questions)} do not belong to exam {exam_id}"
            )
        
        if ExamSubmission.objects.filter(student_id=student_id, exam_id=exam_id).exists():
            raise serializers.ValidationError("Student has already submitted this exam")
        
        return data

    def create(self, validated_data):
        """Create ExamSubmission and all SubmissionAnswers in a transaction"""
        student_id = validated_data['student_id']
        exam_id = validated_data['exam_id']
        answers_data = validated_data['answers']
        
        with transaction.atomic():

            submission = ExamSubmission.objects.create(
                student_id=student_id,
                exam_id=exam_id
            )
            

            submission_answers = []
            for answer_data in answers_data:
                submission_answers.append(
                    SubmissionAnswer(
                        submission=submission,
                        question_id=answer_data['question_id'],
                        selected_alternative_option=answer_data['selected_option']
                    )
                )
            
            SubmissionAnswer.objects.bulk_create(submission_answers)
        
        return submission


class AlternativeResultSerializer(serializers.ModelSerializer):
    """Serializer for alternative options in results"""
    option_letter = serializers.SerializerMethodField()
    
    class Meta:
        model = Alternative
        fields = ['option', 'option_letter', 'content', 'is_correct']
    
    def get_option_letter(self, obj):
        """Convert option number to letter"""
        options = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        return options.get(obj.option, '')


class QuestionResultSerializer(serializers.ModelSerializer):
    """Serializer for question details in results"""
    alternatives = AlternativeResultSerializer(many=True, read_only=True)
    student_answer = serializers.SerializerMethodField()
    student_answer_letter = serializers.SerializerMethodField()
    correct_answer = serializers.SerializerMethodField()
    correct_answer_letter = serializers.SerializerMethodField()
    is_correct = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'content', 'alternatives', 'student_answer', 'student_answer_letter', 
                 'correct_answer', 'correct_answer_letter', 'is_correct']
    
    def get_student_answer(self, obj):
        """Get the student's selected option number"""
        submission_answer = self.context.get('submission_answers', {}).get(obj.id)
        return submission_answer.selected_alternative_option if submission_answer else None
    
    def get_student_answer_letter(self, obj):
        """Get the student's selected option letter"""
        student_answer = self.get_student_answer(obj)
        if student_answer:
            options = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
            return options.get(student_answer, '')
        return None
    
    def get_correct_answer(self, obj):
        """Get the correct option number"""
        try:
            correct_alt = obj.alternatives.get(is_correct=True)
            return correct_alt.option
        except Alternative.DoesNotExist:
            return None
    
    def get_correct_answer_letter(self, obj):
        """Get the correct option letter"""
        correct_answer = self.get_correct_answer(obj)
        if correct_answer:
            options = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
            return options.get(correct_answer, '')
        return None
    
    def get_is_correct(self, obj):
        """Check if student's answer is correct"""
        submission_answer = self.context.get('submission_answers', {}).get(obj.id)
        return submission_answer.is_correct if submission_answer else False


class ExamResultSerializer(serializers.ModelSerializer):
    """Serializer for exam results with detailed question analysis"""
    questions = serializers.SerializerMethodField()
    student_name = serializers.CharField(source='student.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    total_questions = serializers.SerializerMethodField()
    correct_answers = serializers.IntegerField(source='correct_answers_count', read_only=True)
    score_percentage = serializers.FloatField(source='score', read_only=True)
    
    class Meta:
        model = ExamSubmission
        fields = ['id', 'student_name', 'exam_name', 'submitted_at', 'total_questions', 
                 'correct_answers', 'score_percentage', 'questions']
    
    def get_total_questions(self, obj):
        """Get total number of questions in the exam"""
        return obj.answers.count()
    
    def get_questions(self, obj):
        """Get detailed question results"""

        submission_answers = {
            answer.question_id: answer 
            for answer in obj.answers.select_related('question').all()
        }

        exam_questions = obj.exam.examquestion_set.select_related('question').order_by('number')
        questions = [eq.question for eq in exam_questions]
        
        serializer = QuestionResultSerializer(
            questions, 
            many=True, 
            context={'submission_answers': submission_answers}
        )
        return serializer.data