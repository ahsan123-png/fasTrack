from rest_framework import serializers
import random
from userEx.views import *  # Import the helper function

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['first_name', 'last_name', 'email', 'admin_phone', 'admin_gender', 'admin_password']

    def validate_admin_phone(self, value):
        """Clean the phone number before validation."""
        return clean_phone_number(value)

    def create(self, validated_data):
        # Generate unique username using first name and 5 random digits
        first_name = validated_data.get('first_name')
        unique_digits = f"{random.randint(10000, 99999)}"
        username = f"{first_name}{unique_digits}"

        # Clean the phone number
        validated_data['admin_phone'] = clean_phone_number(validated_data['admin_phone'])

        # Set the username and password
        validated_data['username'] = username
        password = validated_data.pop('admin_password')

        # Create the admin user
        admin = Admin(**validated_data)
        admin.set_password(password)
        admin.is_Admin = True
        admin.save()

        return admin
