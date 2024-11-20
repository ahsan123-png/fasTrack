from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from userEx.models import *
from .serializer import *
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.conf import settings
# Step 1: Basic Information
class BasicInformationView(APIView):
    def post(self, request):
        data = request.data
        serializer = JobApplicationSerializer(data=data)
        if serializer.is_valid():
            job_application = serializer.save()  # Save and create new entry
            return Response({
                "status": "success",
                "message": "Job application created successfully",
                "applicant_id": job_application.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Step 2: Position Information
class PositionInformationView(APIView):
    def post(self, request):
        job_application_id = request.data.get('job_application')
        job_application = get_object_or_404(JobApplication, id=job_application_id)
        # Include the `job_application` in the data
        data = request.data
        data['job_application'] = job_application.id
        serializer = PositionInformationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Position Information saved successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Step 3: Experience
class ExperienceView(APIView):
    def post(self, request):
        job_application_id = request.data[0].get('job_application')
        job_application = get_object_or_404(JobApplication, id=job_application_id)
        for experience in request.data:
            experience['job_application'] = job_application_id
        serializer = ExperienceSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Experience saved successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Step 4: Skills & Assessments
class SkillsAssessmentView(APIView):
    def post(self, request):
        job_application_id = request.data.get('job_application')
        job_application = get_object_or_404(JobApplication, id=job_application_id)
        data = request.data
        data['job_application'] = job_application.id
        serializer = SkillsAssessmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Skills Assessment saved successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Step 5: Education
class EducationView(APIView):
    def post(self, request):
        job_application_id = request.data[0].get('job_application')
        job_application = get_object_or_404(JobApplication, id=job_application_id)
        for education in request.data:
            education['job_application'] = job_application_id
        serializer = EducationSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Education saved successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Step 6: Additional Information
class AdditionalInformationView(APIView):
    def post(self, request):
        job_application_id = request.data.get('job_application')
        job_application = get_object_or_404(JobApplication, id=job_application_id)
        data = request.data
        data['job_application'] = job_application.id
        serializer = AdditionalInformationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Additional Information saved successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Step 7 & 8: Media Uploads
class MediaUploadsView(APIView):
    def post(self, request):
        job_application_id = request.data.get('job_application')
        job_application = get_object_or_404(JobApplication, id=job_application_id)
        data = request.data
        data['job_application'] = job_application.id
        serializer = MediaUploadsSerializer(data=data)
        if serializer.is_valid():
            media_upload = serializer.save()
            job_application.is_complete = True
            job_application.save()
            if job_application.is_complete:
                send_application_emails(job_application)
            response_data = {
                "message": "Media uploaded and application completed successfully.",
                "uploaded_files": {
                    "video": media_upload.video.url if media_upload.video else None,
                    "resume": media_upload.resume.url if media_upload.resume else None,
                    "cover_letter": media_upload.cover_letter.url if media_upload.cover_letter else None,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_applicant_data(request, applicant_id):
    if request.method == 'GET':
        try:
            # Get the JobApplication instance by applicant ID
            applicant = JobApplication.objects.get(id=applicant_id)
            # Retrieve related data from all models
            position_info = getattr(applicant, 'position_info', None)
            experiences = applicant.experiences.all()
            skills_assessment = getattr(applicant, 'skills_assessment', None)
            educations = applicant.educations.all()
            additional_info = getattr(applicant, 'additional_info', None)
            media_uploads = getattr(applicant, 'media_uploads', None)
            # Prepare a dictionary to store the applicant's complete data
            applicant_data = {
                "name": applicant.name,
                "email": applicant.email,
                "phone": applicant.phone,
                "address": applicant.address,
                "linkedin_profile": applicant.linkedin_profile,
                "position_applied_for": position_info.position_applied_for if position_info else None,
                "employment_type": position_info.employment_type if position_info else None,
                "preferred_shift": position_info.preferred_shift if position_info else None,
                "applied_date": position_info.applied_date if position_info else None,
                "experiences": [
                    {
                        "job_title": exp.job_title,
                        "company": exp.company,
                        "duration_from": exp.duration_from,
                        "duration_to": exp.duration_to,
                        "key_responsibilities": exp.key_responsibilities,
                    }
                    for exp in experiences
                ],
                "skills_assessment": {
                    "languages": skills_assessment.languages if skills_assessment else None,
                    "tech_skills": skills_assessment.tech_skills if skills_assessment else None,
                    "certificates": skills_assessment.certificates if skills_assessment else None,
                    "tech_experience_description": skills_assessment.tech_experience_description if skills_assessment else None
                } if skills_assessment else None,
                "educations": [
                    {
                        "degree": edu.degree,
                        "institute": edu.institute,
                        "graduation_year": edu.graduation_year,
                    }
                    for edu in educations
                ],
                "additional_info": {
                    "why_interested": additional_info.why_interested if additional_info else None,
                    "strong_fit_reason": additional_info.strong_fit_reason if additional_info else None,
                    "eligible_to_work": additional_info.eligible_to_work if additional_info else None,
                    "source_of_opportunity": additional_info.source_of_opportunity if additional_info else None
                } if additional_info else None,
                "media_uploads": {
                    "video": media_uploads.video.url if media_uploads and media_uploads.video else None,
                    "resume": media_uploads.resume.url if media_uploads and media_uploads.resume else None,
                    "cover_letter": media_uploads.cover_letter.url if media_uploads and media_uploads.cover_letter else None
                } if media_uploads else None
            }
            # Return JSON response
            return JsonResponse(applicant_data, safe=False)
        except JobApplication.DoesNotExist:
            return JsonResponse({"error": "Applicant not found"}, status=404)
    # If the request method is not GET
    return JsonResponse({"error": "Method not allowed"}, status=405)

#================= get Data by ID ==================#
class GetAllApplicantsView(APIView):
    def get(self, request):
        job_applications = JobApplication.objects.prefetch_related(
            Prefetch('experiences', queryset=Experience.objects.only(
                'job_title', 'company', 'duration_from', 'duration_to', 'key_responsibilities'
            )),
            Prefetch('educations', queryset=Education.objects.only(
                'degree', 'institute', 'graduation_year'
            ))
        ).select_related(
            'skills_assessment', 'additional_info', 'media_uploads', 'position_info'
        )
        applicants_data = []
        for applicant in job_applications:
            applicant_data = {
                "applicant_id": applicant.id,  # Add the applicant_id here
                "name": applicant.name,
                "email": applicant.email,
                "phone": applicant.phone,
                "address": applicant.address,
                "linkedin_profile": applicant.linkedin_profile,
                "is_complete": applicant.is_complete,
            }
            if hasattr(applicant, 'position_info') and applicant.position_info:
                applicant_data.update({
                    "position_applied_for": applicant.position_info.position_applied_for,
                    "employment_type": applicant.position_info.employment_type,
                    "preferred_shift": applicant.position_info.preferred_shift,
                    "applied_date": applicant.position_info.applied_date,
                })
            else:
                applicant_data.update({
                    "position_applied_for": None,
                    "employment_type": None,
                    "preferred_shift": None,
                    "applied_date": None,
                })

            applicant_data['experiences'] = [
                {
                    "job_title": exp.job_title,
                    "company": exp.company,
                    "duration_from": exp.duration_from,
                    "duration_to": exp.duration_to,
                    "key_responsibilities": exp.key_responsibilities,
                }
                for exp in applicant.experiences.all()
            ]
            if hasattr(applicant, 'skills_assessment') and applicant.skills_assessment:
                applicant_data['skills_assessment'] = {
                    "languages": applicant.skills_assessment.languages,
                    "tech_skills": applicant.skills_assessment.tech_skills,
                    "certificates": applicant.skills_assessment.certificates,
                    "tech_experience_description": applicant.skills_assessment.tech_experience_description,
                }
            else:
                applicant_data['skills_assessment'] = None
            applicant_data['educations'] = [
                {
                    "degree": edu.degree,
                    "institute": edu.institute,
                    "graduation_year": edu.graduation_year,
                }
                for edu in applicant.educations.all()
            ]
            if hasattr(applicant, 'additional_info') and applicant.additional_info:
                applicant_data['additional_info'] = {
                    "why_interested": applicant.additional_info.why_interested,
                    "strong_fit_reason": applicant.additional_info.strong_fit_reason,
                    "eligible_to_work": applicant.additional_info.eligible_to_work,
                    "source_of_opportunity": applicant.additional_info.source_of_opportunity,
                }
            else:
                applicant_data['additional_info'] = None
            if hasattr(applicant, 'media_uploads') and applicant.media_uploads:
                applicant_data['media_uploads'] = {
                    "video": applicant.media_uploads.video.url if applicant.media_uploads.video else None,
                    "resume": applicant.media_uploads.resume.url if applicant.media_uploads.resume else None,
                    "cover_letter": applicant.media_uploads.cover_letter.url if applicant.media_uploads.cover_letter else None,
                }
            else:
                applicant_data['media_uploads'] = None
            applicants_data.append(applicant_data)
        return Response(applicants_data, status=status.HTTP_200_OK)


# =================== send mails to admins and applicants ====================================
def send_application_emails(job_application):
    # Send email to applicant
    subject_applicant = f"Your Job Application is Complete, {job_application.name}!"
    message_applicant = (
        f"Dear {job_application.name},\n\n"
        f"Thank you for submit your application for the {job_application.position_info.position_applied_for} position. "
        f"We have successfully received all the required information and will review your application soon.\n\n"
        f"Best regards,\n"
        f"fastrak Connect Recruitment Team"
    )
    try:
        send_mail(subject_applicant, message_applicant, settings.EMAIL_HOST_USER, [job_application.email])
    except Exception as e:
        print(f"Failed to send email to applicant: {str(e)}")

    # Send email to admin
    subject_admin = f"New Job Application Completed: {job_application.name}"
    message_admin = (
        f"Dear Admin,\n\n"
        f"The job application for {job_application.name} has been completed. Here are the details:\n\n"
        f"Name: {job_application.name}\n"
        f"Email: {job_application.email}\n"
        f"Phone: {job_application.phone}\n"
        f"Position Applied For: {job_application.position_info.position_applied_for}\n\n"
        f"Please review the application at your earliest convenience.\n\n"
        f"Best regards,\n"
        f"The System"
    )
    try:
        send_mail(subject_admin, message_admin, settings.EMAIL_HOST_USER, [settings.ADMIN_EMAIL])
    except Exception as e:
        print(f"Failed to send email to admin: {str(e)}")