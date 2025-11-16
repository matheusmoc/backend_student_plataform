from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from question.models import Question, Alternative


from question.utils import QuestiosTypeChoices


class AlternativeInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not hasattr(self, 'instance') or not self.instance:
            return
        if self.instance.selection_type == QuestiosTypeChoices.SINGLE:
            correct_count = 0
            for form in self.forms:
                if not hasattr(form, 'cleaned_data'):
                    continue
                data = form.cleaned_data
                if data.get('DELETE'):
                    continue
                if data.get('is_correct'):
                    correct_count += 1
            if correct_count > 1:
                raise ValidationError('Questões de escolha única só podem ter uma alternativa correta.')


class AlternativeInline(admin.TabularInline):
    model = Alternative
    min_num = 1
    max_num = 5
    ordering = ('option',)
    formset = AlternativeInlineFormSet


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AlternativeInline]
