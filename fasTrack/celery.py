from celery import Celery
from schedule import tasks as schedule_tasks  # Explicitly import tasks from 'schedule'
import os
from celery.schedules import crontab 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fasTrack.settings')
app = Celery('fasTrack')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = 'redis://13.60.13.74:6379/0'
# Manually import the tasks
app.tasks.register(schedule_tasks.schedule_expiry_notification)
app.tasks.register(schedule_tasks.send_document_expiry_notification)
app.tasks.register(schedule_tasks.notify_user)
app.conf.beat_schedule = {
    'notify-users-every-day': {
        'task': 'schedule.tasks.notify_user',
        'schedule': crontab(hour=8, minute=0),
    },
}
