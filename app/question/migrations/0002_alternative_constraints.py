from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternative',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alternative',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alternatives', to='question.question'),
        ),
        migrations.AddConstraint(
            model_name='alternative',
            constraint=models.UniqueConstraint(fields=('question', 'option'), name='unique_question_option'),
        ),
        migrations.AddConstraint(
            model_name='alternative',
            constraint=models.UniqueConstraint(condition=Q(('is_correct', True)), fields=('question',), name='unique_correct_alternative_per_question'),
        ),
    ]
