from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from userEx.models import *
from .serializer import *
from django.shortcuts import get_object_or_404
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
            serializer.save()
            return Response({"message": "Media Uploads saved successfully."}, status=status.HTTP_201_CREATED)
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
class ApplicantDetailView(APIView):
    def get(self, request, applicant_id):
        try:
            # Fetch the JobApplication instance by applicant_id
            applicant = get_object_or_404(JobApplication, id=applicant_id)
            position_info = applicant.position_info
            experiences = applicant.experiences.all()
            skills_assessment = applicant.skills_assessment
            educations = applicant.educations.all()
            additional_info = applicant.additional_info
            media_uploads = applicant.media_uploads
            position_info_serializer = PositionInformationSerializer(position_info)
            experiences_serializer = ExperienceSerializer(experiences, many=True)
            skills_assessment_serializer = SkillsAssessmentSerializer(skills_assessment)
            educations_serializer = EducationSerializer(educations, many=True)
            additional_info_serializer = AdditionalInformationSerializer(additional_info)
            media_uploads_serializer = MediaUploadsSerializer(media_uploads)
            applicant_data = {
                "name": applicant.name,
                "email": applicant.email,
                "phone": applicant.phone,
                "address": applicant.address,
                "linkedin_profile": applicant.linkedin_profile,
                "position_info": position_info_serializer.data,
                "experiences": experiences_serializer.data,
                "skills_assessment": skills_assessment_serializer.data,
                "educations": educations_serializer.data,
                "additional_info": additional_info_serializer.data,
                "media_uploads": media_uploads_serializer.data,
            }
            return Response(applicant_data, status=status.HTTP_200_OK)
        except JobApplication.DoesNotExist:
            return Response({"error": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)