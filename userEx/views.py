from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClientSerializer
from .models import *
from datetime import datetime

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


class CreateOrderAPIView(APIView):
    def post(self, request, *args, **kwargs):
        client_id = request.data.get('client_id')
        order_date = request.data.get('order_date')
        if not client_id or not order_date:
            return Response({"error": "client_id and order_date are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"error": f"Client with client_id '{client_id}' does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Please use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.create(
            client=client,
            order_date=order_date
        )
        return Response({
            "order_id": order.order_id,
            "sales_order_number": order.sales_order_number,
            "order_date": order.order_date,
            "client_id": client.client_id
        }, status=status.HTTP_201_CREATED)