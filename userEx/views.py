from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClientSerializer
from .models import *

class CreateClientAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract data from the request body
        client_data = {
            'client_email': request.data.get('client_email'),
            'client_name': request.data.get('client_name'),  # Use 'client_name' here
            'address': request.data.get('address'),
            'phone_number': request.data.get('phone_number'),
            'business_name': request.data.get('business_name'),
            'country': request.data.get('country'),
        }
        # Create the client using the serializer
        client_serializer = ClientSerializer(data=client_data)
        if client_serializer.is_valid():
            # Save the client (this will also generate a client_id)
            client = client_serializer.save()
            order = Order.objects.create(
                client=client
            )
            return Response({
                "client": client_serializer.data,
                "order_id": order.order_id,  # Add order_id to the response
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(client_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
