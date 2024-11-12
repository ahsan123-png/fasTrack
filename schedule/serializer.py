# your_app/serializers.py
from rest_framework import serializers
from userEx.models import *

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
