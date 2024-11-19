
from django.contrib import admin
from django.urls import path , include
from .views import *

urlpatterns = [
    path('create/', admin_signup_view, name='admin-create'),
    path('login/', admin_login, name='admin-login')
]
