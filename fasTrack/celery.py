import os
from celery import Celery
from schedule import task as schedule_tasks  # Explicitly import tasks from 'schedule'
from celery.schedules import crontab 
# print("DJANGO_SETTINGS_MODULE:", os.getenv('DJANGO_SETTINGS_MODULE'))
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'fasTrack.settings'
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
