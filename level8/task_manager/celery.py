import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

app = Celery('task_manager', broker="redis://localhost:6379")

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.timezone = 'Asia/Kolkata'

app.conf.beat_schedule = {
    'send_unsent_reports': {
        'task': 'check_unsent_reports',
        'schedule': 60.0,
    }
}