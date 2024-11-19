import random
from rest_framework import serializers
from userEx.models import Admin  # Update if your models are in another location
from userEx.views import clean_phone_number
from rest_framework.authtoken.models import Token  # For token generation

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['first_name', 'last_name', 'email', 'admin_phone', 'admin_gender', 'admin_password','is_Admin']
        extra_kwargs = {'admin_password': {'write_only': True}}  # Password is write-only
    def validate_email(self, value):
        """Check if email already exists."""
        if Admin.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value
    def validate_admin_phone(self, value):
        """Clean and validate phone number."""
        return clean_phone_number(value)
    def create(self, validated_data):
        # Generate unique username using first name and 5 random digits
        first_name = validated_data.get('first_name')
        unique_digits = f"{random.randint(10000, 99999)}"
        username = f"{first_name}{unique_digits}"
        validated_data['admin_phone'] = clean_phone_number(validated_data['admin_phone'])
        password = validated_data.pop('admin_password')
        admin = Admin(**validated_data)
        admin.username = username
        admin.set_password(password)  # Hashes the password
        admin.is_Admin = True
        admin.save()
        token, created = Token.objects.get_or_create(user=admin)

        return {"admin": admin, "token": token.key}

# =============== Admin Login =============
class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True)
    def validate(self, data):
        email = data.get('email')
        password = data.get('admin_password')
        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            raise serializers.ValidationError("No admin found with this email.")
        if not admin.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
        return {"admin": admin}