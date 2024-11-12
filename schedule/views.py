from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.shortcuts import redirect
from schedule.task import schedule_expiry_notification
from userEx.models import *
from .serializer import *
from datetime import datetime, timedelta
from django.conf import settings
import redis
from rest_framework.response import Response
from rest_framework import viewsets

def get_google_drive_service(credentials_dict):
    credentials = Credentials(**credentials_dict)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    return build('drive', 'v3', credentials=credentials)
def google_drive_oauth(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_JSON,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(authorization_url)

# Callback to handle the response from Google
def google_drive_callback(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_JSON,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)  # Convert to dict for session storage
    return JsonResponse({'message': 'Google Drive connected successfully'})

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
@csrf_exempt
def upload_document(request):
    if request.method == 'POST':
        credentials_dict = request.session.get('credentials')
        if not credentials_dict:
            return JsonResponse({'error': 'User not authenticated. Please connect to Google Drive first.'}, status=403)
        credentials = Credentials(**credentials_dict)
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file uploaded.'}, status=400)
        title = request.POST.get('title')
        description = request.POST.get('description')
        expiry_date = request.POST.get('expiry_date')
        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'error': 'Invalid expiry date format. Use YYYY-MM-DD.'}, status=400)
        if not title or not description or not expiry_date:
            return JsonResponse({'error': 'All fields are required.'}, status=400)
        credentials = Credentials(**credentials_dict)
        service = get_google_drive_service(credentials)
        file_metadata = {
            'name': title,
            'mimeType': file.content_type
        }
        media = MediaFileUpload(file.temporary_file_path(), mimetype=file.content_type)
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        document_id = uploaded_file.get('id')
        Document.objects.create(
            title=title,
            description=description,
            document_id=document_id,
            expiry_date=expiry_date
        )

        return JsonResponse({'document_id': document_id}, status=201)
    return JsonResponse({'error': 'Invalid request'}, status=400)

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def create(self, request, args, *kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save(user=request.user)
        self.send_expiry_notification(document)
        return Response(serializer.data)