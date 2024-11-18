# driveHandler/celery.py
from celery import Celery
from celery.schedules import crontab
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fasTrack.settings')
app = Celery('schedule')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'notify-users-every-day': {
        'task': 'your_app.tasks.notify_user',
        'schedule': crontab(hour=8, minute=0),
    },
}

