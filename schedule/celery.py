# schedule/celery.py

from __future__ import absolute_import, unicode_literals

# Import the main Celery application from fasTrack project
from fasTrack.celery import app as celery_app

# This file can be left empty or used for app-specific Celery configurations
__all__ = ('celery_app',)


