from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['client_id']  # Mark client_id as read-only

