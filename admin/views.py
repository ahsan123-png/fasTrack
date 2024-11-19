from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from .serializer import *

@csrf_exempt
def admin_create_view(request):
    if request.method == 'POST':
        try:
            # Parse incoming JSON data
            data = JSONParser().parse(request)
            serializer = AdminSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"message": "Admin created successfully!", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
