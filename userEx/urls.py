# urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('create-client/', CreateClientAPIView.as_view(), name='create-client'),
    path('create-order/', CreateOrderAPIView.as_view(), name='create-order'),
]
