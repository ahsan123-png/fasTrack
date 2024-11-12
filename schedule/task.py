from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from userEx.models import *
import redis

@shared_task
def schedule_expiry_notification(document_id):
    try:
        document = Document.objects.get(id=document_id)
        notify_date = document.expiry_date - timedelta(weeks=2)

        if notify_date > timezone.now():
            send_document_expiry_notification.apply_async(args=[document_id], eta=notify_date)
        else:
            # If notification date is in the past, send it immediately
            send_document_expiry_notification(document_id)

    except Document.DoesNotExist:
        print(f"Document with id {document_id} does not exist.")

@shared_task
def send_document_expiry_notification(document_id):
    try:
        document = Document.objects.get(id=document_id)
        send_mail(
            subject=f'Document "{document.title}" Expiry Notification',
            message=f'Your document "{document.title}" will expire on {document.expiry_date.strftime("%Y-%m-%d")}.',
            from_email='noreply@yourdomain.com',
            recipient_list=[document.user.email],
        )
        print(f"Notification sent for document {document.title} to {document.user.email}")
    except Document.DoesNotExist:
        print(f"Document with id {document_id} does not exist.")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
