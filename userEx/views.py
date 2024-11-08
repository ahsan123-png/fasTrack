from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import stripe
from .serializers import *
from .models import *
from datetime import datetime
from rest_framework.decorators import api_view
from decimal import Decimal
stripe.api_key = settings.STRIPE_SECRET_KEY
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
        # Validate input
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
        order.save()
        return Response({
            "order_id": order.order_id,
            "sales_order_number": order.sales_order_number, 
            "order_date": order.order_date,
            "client_id": client.client_id
        }, status=status.HTTP_201_CREATED)
# Assume these models are already defined
@api_view(['POST'])
def serviceSelectionView(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    services_data = request.data.get('services_selected')
    billing_data = request.data.get('billing_details')
    billing_cycle = billing_data.get('billing_cycle', 'monthly')
    payment_method = billing_data.get('payment_method', 'bank_transfer')
    service_plan_id = services_data.get('service_plan', {}).get('id')
    multilingual_agents = services_data.get('multilingual_support', {}).get('agents', 0)
    after_hours = services_data.get('after_hours_holiday_premium', {}).get('hours', 0)
    technical_hours = services_data.get('technical_support', {}).get('hours', 0)
    fastrak_price = services_data.get('fastrak_briefcase', {}).get('price_per_month', 0)
    starter_prosiwo_price = services_data.get('starter_prosiwo', {}).get('price_per_month', 0)
    try:
        service_plan = ServicePlan.objects.get(id=service_plan_id)
    except ServicePlan.DoesNotExist:
        return Response({"error": "Service plan not found"}, status=status.HTTP_404_NOT_FOUND)
    multilingual_price = Decimal(multilingual_agents) * Decimal('100.00')  # $100 per multilingual agent
    after_hours_price = Decimal(after_hours) * Decimal('10.00')  # $10 per hour for after-hours support
    technical_price = Decimal(technical_hours) * Decimal('10.00')  # $10 per hour for technical support
    fastrak_price = Decimal(fastrak_price)  # price per month
    starter_prosiwo_price = Decimal(starter_prosiwo_price)
    total_price = service_plan.price + multilingual_price + after_hours_price + technical_price + fastrak_price + starter_prosiwo_price
    discount = Decimal('0.00')
    if billing_cycle == 'annual':
        discount = total_price * Decimal('0.10')
        total_price -= discount
    processing_fee = Decimal('0.00')
    if payment_method == 'credit_card':
        processing_fee = total_price * Decimal('0.02')  # 2% processing fee for credit card
        total_price += processing_fee
    service_selection, created = ServiceSelection.objects.get_or_create(
        order=order,
        defaults={
            'service_plan': service_plan,
            'multilingual_support_agents': multilingual_agents,
            'after_hours_support_hours': after_hours,
            'technical_support_hours': technical_hours,
            'fastrak_briefcase_price': fastrak_price,
            'starter_prosiwo_price': starter_prosiwo_price
        }
    )
    order.total_price = service_selection.calculate_total()
    order.save()
    billing, created = Billing.objects.get_or_create(
        order=order,
        defaults={
            'client': order.client,
            'billing_cycle': billing_cycle,
            'payment_method': payment_method,
            'discount': discount,
            'service_plan': service_plan,
        }
    )
    billing.total_amount = total_price
    billing.save()
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Convert the total price to cents
            currency='usd',  # You can change this to your desired currency
            metadata={'order_id': order.id},
        )
        order.payment_intent_client_secret = payment_intent.client_secret
        order.save()
        response_data = {
            "order_id": order_id,
            "client": {
                "client_id": order.client.client_id,
                "client_email": order.client.client_email,
                "business_name": order.client.business_name,
            },
            "services_selected": {
                "service_plan": {
                    "name": service_plan.name,
                    "price": service_plan.price,
                },
                "multilingual_support": {
                    "agents": multilingual_agents,
                    "price_per_agent": 100.00,
                    "total_price": multilingual_price,
                },
                "after_hours_holiday_premium": {
                    "hours": after_hours,
                    "price_per_hour": 10.00,
                    "total_price": after_hours_price,
                },
                "technical_support": {
                    "hours": technical_hours,
                    "price_per_hour": 10.00,
                    "total_price": technical_price,
                },
                "fastrak_briefcase": {
                    "price_per_month": fastrak_price,
                },
                "starter_prosiwo": {
                    "price_per_month": starter_prosiwo_price,
                }
            },
            "billing_details": {
                "billing_cycle": billing_cycle,
                "payment_method": payment_method,
                "discount": discount,
                "processing_fee": processing_fee,
            },
            "total_amount": {
                "subtotal": total_price + discount,
                "total_after_discount": total_price,
            },
            "payment_intent_client_secret": payment_intent.client_secret
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_service_plan(request):
    if request.method == 'POST':
        serializer = ServicePlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)