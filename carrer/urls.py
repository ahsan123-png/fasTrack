from django.urls import path
from .views import *

urlpatterns = [
    path('basic_information/', BasicInformationView.as_view(), name='basic_information'),
    path('position_information/', PositionInformationView.as_view(), name='position_information'),
    path('experience/', ExperienceView.as_view(), name='experience'),
    path('skills_assessment/', SkillsAssessmentView.as_view(), name='skills_assessment'),
    path('education_view/', EducationView.as_view(), name='education_view'),
    path('additional_information/', AdditionalInformationView.as_view(), name='additional_information'),
    path('Media_uploadsView/', MediaUploadsView.as_view(), name='Media_uploadsView-8'),
    path('get/all/<int:applicant_id>', get_applicant_data, name='get_applicant_data'),
    path('get/all', GetAllApplicantsView.as_view(), name='applicant-detail'),
    # ========= Update APIs =========
    path('update-basic-info/<int:pk>/', BasicInformationUpdateView.as_view(), name='update-basic-info'),
    path('update-position-info/<int:pk>/', PositionInformationUpdateView.as_view(), name='update-position-info'),
    path('update-experience/<int:job_application_id>/', ExperienceUpdateView.as_view(), name='update-experience'),
    path('update-skills/<int:pk>/', SkillsAssessmentUpdateView.as_view(), name='update-skills'),
    path('update-education/<int:education_id>/', EducationUpdateView.as_view(), name='update-education'),
    path('update-additional-info/<int:pk>/', AdditionalInformationUpdateView.as_view(), name='update-additional-info'),
    path('update-media/<int:pk>/', MediaUploadsUpdateView.as_view(), name='update-media'),
]
