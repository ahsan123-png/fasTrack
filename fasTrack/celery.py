import os
from celery import shared_task
from celery import Celery
from celery.schedules import crontab 


# Set default Django settings module for the 'celery' program
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'fasTrack.settings'

app = Celery('fasTrack')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Define periodic task schedule
app.conf.beat_schedule = {
    'notify-users-every-day': {
        'task': 'schedule.tasks.notify_user',
        'schedule': crontab(hour=8, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@shared_task
def notify_user():
    print("Notification task executed!")