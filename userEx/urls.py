# urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('create-client/', CreateClientAPIView.as_view(), name='create-client'),
    path('create-order/', CreateOrderAPIView.as_view(), name='create-order'),
    path('create-order-billing/<int:order_id>/', serviceSelectionView, name='serviceSelectionView-order'),
    path('service_plain/', create_service_plan, name='create_service_plan'),
]
