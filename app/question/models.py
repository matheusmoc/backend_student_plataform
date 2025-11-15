from django.db import models
from django.core.exceptions import ValidationError

from question.utils import AlternativesChoices, QuestiosTypeChoices


class Question(models.Model):

    content = models.TextField()
    selection_type = models.CharField(
        max_length=10,
        choices=QuestiosTypeChoices.choices,
        default=QuestiosTypeChoices.SINGLE,
        db_index=True,
        help_text='Define se a questão aceita uma única resposta ou múltiplas.'
    )

    def __str__(self):
        return self.content


class Alternative(models.Model):
    question = models.ForeignKey(Question, related_name='alternatives', on_delete=models.CASCADE)
    content = models.TextField()
    option = models.IntegerField(choices=AlternativesChoices)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('question', 'option')
        ordering = ['option']

    def __str__(self):
        return f'{self.question_id} - {self.get_option_display()}: {self.content[:30]}'

    def clean(self):
        if self.is_correct and self.question_id:
            try:
                question = self.question  
                if question.selection_type == QuestiosTypeChoices.SINGLE:
                    qs = Alternative.objects.filter(question_id=self.question_id, is_correct=True)
                    if self.pk:
                        qs = qs.exclude(pk=self.pk)
                    if qs.exists():
                        raise ValidationError('Questões de escolha única só podem ter uma alternativa correta.')
            except Question.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
