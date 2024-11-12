from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
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
# ===================== create order =================
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
        order.save()
        return Response({
            "order_pk_id": order.id,
            "order_id": order.order_id,
            "sales_order_number": order.sales_order_number, 
            "order_date": order.order_date,
            "client_id": client.client_id
        }, status=status.HTTP_201_CREATED)
# ===================== services selection and calculation =================
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
    advanced_prosiwo_price = services_data.get('advanced_prosiwo', {}).get('price_per_month', 0)
    try:
        service_plan = ServicePlan.objects.get(id=service_plan_id)
    except ServicePlan.DoesNotExist:
        return Response({"error": "Service plan not found"}, status=status.HTTP_404_NOT_FOUND)
    multilingual_price = Decimal(multilingual_agents) * Decimal('200.00')
    after_hours_price = Decimal(after_hours) * Decimal('10.00') 
    technical_price = Decimal(technical_hours) * Decimal('10.00')  
    fastrak_price = Decimal(fastrak_price)
    starter_prosiwo_price = Decimal(starter_prosiwo_price)
    advanced_prosiwo_price=Decimal(advanced_prosiwo_price)
    total_price = (service_plan.price + multilingual_price + after_hours_price +
                technical_price + fastrak_price + starter_prosiwo_price + advanced_prosiwo_price)
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
    billing.discount = discount
    billing.save()
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100), 
            currency='usd', 
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
                },
                 "advanced_prosiwo": {
                "price_per_month": advanced_prosiwo_price,
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
# ================== stripe webhook =================
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    # Get the signature sent by Stripe in the headers
    sig_header = request.headers.get('Stripe-Signature')
    # Your webhook secret, generated from the Stripe Dashboard
    endpoint_secret = 'whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    try:
        # Verify the webhook signature using the payload and the secret
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
    event_type = event['type']
    if event_type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']  # Custom metadata field with the order ID
        amount_received = payment_intent['amount_received']  # Amount received (in cents)
        client_email = payment_intent['receipt_email']  # The email associated with the payment
        # Retrieve the order from the database using the order ID from the metadata
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        # Update the order status to 'Paid' since the payment succeeded
        order.status = 'Paid'
        order.total_price = amount_received / 100.0  # Convert cents to dollars
        order.save()
        send_invoice_email(order, client_email)
        # Send a confirmation email (optional, depending on your use case)
        # send_confirmation_email(order)  # Implement your email function as needed
        # Return a success response to Stripe (200 OK)
        return JsonResponse({'message': 'Payment successful and order updated'}, status=status.HTTP_200_OK)
    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']
        failure_message = payment_intent['last_payment_error']['message']
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        order.status = 'Payment Failed'
        order.save()
        return JsonResponse({'message': 'Payment failed and order updated'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Event type not handled'}, status=status.HTTP_200_OK)
# ================== send mail =================
def send_invoice_email(order, client_email):
    # Prepare the email subject and body using an HTML template
    subject = f"Invoice for Order {order.id}"
    message = render_to_string('emails/order_invoice.html', {
        'order_id': order.id,
        'customer_name': order.client.business_name,
        'status': order.status,
        'total_price': order.total_price,
        'service_plan_name': order.service_plan.name,
        'service_plan_price': order.service_plan.price,
        'multilingual_agents': order.multilingual_support_agents,
        'multilingual_support_price': order.multilingual_support_agents * 100.00,
        'after_hours': order.after_hours_support_hours,
        'after_hours_support_price': order.after_hours_support_hours * 10.00,
        'technical_support_hours': order.technical_support_hours,
        'technical_support_price': order.technical_support_hours * 10.00,
        'fastrak_price': order.fastrak_briefcase_price,
        'starter_prosiwo_price': order.starter_prosiwo_price,
    })

    # Send the email
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # From email (use the email in your settings)
        [client_email],  # To email (use the email provided by Stripe)
        fail_silently=False,
    )