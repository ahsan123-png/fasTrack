# Create your views here.
from rest_framework import serializers
from userEx.models import *

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['name', 'email', 'phone', 'address', 'linkedin_profile']

class PositionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionInformation
        fields = ['job_application', 'position_applied_for', 'employment_type', 'preferred_shift', 'applied_date']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['job_application', 'job_title', 'company', 'duration_from', 'duration_to', 'key_responsibilities']

class SkillsAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsAssessment
        fields = ['job_application', 'languages', 'tech_skills', 'certificates', 'tech_experience_description']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['job_application', 'degree', 'institute', 'graduation_year']

class AdditionalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalInformation
        fields = ['job_application', 'why_interested', 'strong_fit_reason', 'eligible_to_work', 'source_of_opportunity']

class MediaUploadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaUploads
        fields = ['job_application', 'video', 'resume', 'cover_letter']
