from django.db import models
from django.utils import timezone

from question.models import Question
from student.models import Student


class Exam(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question, through='ExamQuestion', related_name='questions')

    def __str__(self):
        return self.name


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('exam', 'number')
        constraints = [
            models.UniqueConstraint(fields=['exam', 'question'], name='uq_exam_question_unique_per_exam'),
        ]
        ordering = ['number']

    def __str__(self):
        return f'{self.question} - {self.exam}'


class ExamSubmission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('student', 'exam')
    
    def __str__(self):
        return f'{self.student.name} - {self.exam.name}'
    
    @property
    def score(self):
        """Calculate the score percentage for this submission"""
        total_questions = self.answers.count()
        if total_questions == 0:
            return 0
        
        correct_answers = sum(1 for answer in self.answers.all() if answer.is_correct)
        return round((correct_answers / total_questions) * 100, 2)
    
    @property 
    def correct_answers_count(self):
        """Count of correct answers"""
        return sum(1 for answer in self.answers.all() if answer.is_correct)


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(ExamSubmission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_alternative_option = models.IntegerField()  #(1-5 / A-E)
    
    class Meta:
        unique_together = ('submission', 'question')
    
    @property
    def is_correct(self):
        """Check if the selected answer is correct"""
        try:
            correct_alternative = self.question.alternatives.get(is_correct=True)
            return self.selected_alternative_option == correct_alternative.option
        except:
            return False
    
    def __str__(self):
        return f'{self.submission} - Q{self.question.id}: Option {self.selected_alternative_option}'
