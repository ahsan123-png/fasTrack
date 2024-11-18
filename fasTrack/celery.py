# fasTrack/celery.py

from celery import Celery
from celery.schedules import crontab  # Importing crontab for scheduling periodic tasks
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fasTrack.settings')

# Create Celery application instance
app = Celery('fasTrack')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in Django apps
app.autodiscover_tasks()

# Celery Beat schedule (example of using crontab)
app.conf.beat_schedule = {
    'notify-users-every-day': {
        'task': 'schedule.tasks.notify_user',  # Reference to the task
        'schedule': crontab(hour=8, minute=0),  # Every day at 08:00 AM
    },
}
