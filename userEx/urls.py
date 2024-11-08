# urls.py
from django.urls import path
from .views import CreateClientAPIView
urlpatterns = [
    path('create-client/', CreateClientAPIView.as_view(), name='create-client'),
]
