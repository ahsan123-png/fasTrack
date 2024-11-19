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
]
