from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .serializer import *
# views
@csrf_exempt
def admin_signup_view(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = AdminSerializer(data=data)
        if serializer.is_valid():
            result = serializer.save()
            admin = result["admin"]
            token = result["token"]
            response_data = {
                "message": "Admin created successfully!",
                "data": {
                    "first_name": admin.first_name,
                    "last_name": admin.last_name,
                    "email": admin.email,
                    "admin_phone": admin.admin_phone,
                    "admin_gender": admin.admin_gender,
                    "admin_password": admin.admin_password,
                    "is_Admin": admin.is_Admin,
                },
                "token": token,
            }
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
# ================ Admin Login ================
@api_view(['POST'])
def admin_login(request):
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.validated_data['admin']
        token, created = Token.objects.get_or_create(user=admin)
        return Response({
            "message": "Login successful",
            "admin": {
                "first_name": admin.first_name,
                "last_name": admin.last_name,
                "email": admin.email,
                "admin_phone": admin.admin_phone,
                "admin_gender": admin.admin_gender,
                "is_Admin": admin.is_Admin,
            },
            "token": token.key
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)