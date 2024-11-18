from celery import Celery
from celery.schedules import crontab  # Importing crontab for scheduling periodic tasks
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fasTrack.settings')
app = Celery('fasTrack')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks('schedule')
app.conf.beat_schedule = {
    'notify-users-every-day': {
        'task': 'schedule.tasks.notify_user',
        'schedule': crontab(hour=8, minute=0), 
    },
}
