from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_examsubmission_submissionanswer'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='examquestion',
            constraint=models.UniqueConstraint(fields=('exam', 'question'), name='uq_exam_question_unique_per_exam'),
        ),
    ]
