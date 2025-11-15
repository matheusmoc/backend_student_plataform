from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0002_alternative_constraints'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='selection_type',
            field=models.CharField(
                choices=[('SINGLE', 'Single choice'), ('MULTIPLE', 'Multiple choice')],
                db_index=True,
                default='SINGLE',
                max_length=10,
                help_text='Define se a questão aceita uma única resposta ou múltiplas.'
            ),
        ),
        migrations.RemoveConstraint(
            model_name='alternative',
            name='unique_correct_alternative_per_question',
        ),
    ]
