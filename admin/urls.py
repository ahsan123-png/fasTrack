
from django.contrib import admin
from django.urls import path , include
from .views import *

urlpatterns = [
    path('create/', admin_create_view, name='admin-create'),
]
