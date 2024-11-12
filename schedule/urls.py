# your_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from userEx.views import *
from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('google-drive-oauth/', google_drive_oauth, name='google_drive_oauth'),
    path('google-drive-callback/', google_drive_callback, name='google_drive_callback'),
]

