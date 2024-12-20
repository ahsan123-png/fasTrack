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
        fields = '__all__'

class ExperienceSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(required=False, allow_null=True)
    company = serializers.CharField(required=False, allow_null=True)
    duration_from = serializers.DateField(required=False, allow_null=True)
    duration_to = serializers.DateField(required=False, allow_null=True)
    key_responsibilities = serializers.CharField(required=False, allow_null=True)

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
