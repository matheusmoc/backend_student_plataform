import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medway_api.settings')

app = Celery('medway_api')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Fallback to environment variables if not set by settings
if not app.conf.broker_url:
    app.conf.broker_url = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
if not app.conf.result_backend:
    app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Reasonable defaults
app.conf.task_acks_late = app.conf.task_acks_late if app.conf.task_acks_late is not None else True
app.conf.worker_prefetch_multiplier = app.conf.worker_prefetch_multiplier or int(os.getenv('CELERY_WORKER_PREFETCH_MULTIPLIER', '1'))
app.conf.task_time_limit = app.conf.task_time_limit or int(os.getenv('CELERY_TASK_TIME_LIMIT', '300'))
app.conf.task_soft_time_limit = app.conf.task_soft_time_limit or int(os.getenv('CELERY_TASK_SOFT_TIME_LIMIT', '240'))

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
