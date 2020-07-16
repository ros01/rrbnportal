from django.urls import path
from django.shortcuts import render
from . import views
from .views import (
    
    RegistrationListView,
    InspectionScheduleListView,
    InspectionCreateView,
    InspectionCompletedListView,
    LicenseIssueListView,
    LicenseDetailView,
    IssueLicenseView,
    LicensesListView,
    GeneratePdfView,
    RegisteredHospitalsListView,
    RegisterdHospitalsDetailView,
   
)

# Create your views here.


app_name = 'monitoring'


urlpatterns = [
    path('', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('registration_list/', RegistrationListView.as_view(), name='registration_list'),
    path('<uuid:id>', views.vet_application, name='vet_application'),
    path('<uuid:id>/approve/', views.approve, name='approve'),
    path('<uuid:id>/reject/', views.reject, name='reject'),
    path('inspection_list/', InspectionScheduleListView.as_view(), name='inspection_list'),
    path('<uuid:id>/inspection_schedule/', InspectionCreateView.as_view(), name='inspection_schedule'),
    path('inspections_list/', InspectionCompletedListView.as_view(), name='inspections_list'),
    path('<uuid:id>/verify/', views.verify, name='verify'),
    path('<uuid:id>/view_report/', views.view_report, name='view_report'),
    path('<uuid:id>/approve_report/', views.approve_report, name='approve_report'),
    path('<uuid:id>/reject_report/', views.reject_report, name='reject_report'),
    path('license_list/', LicenseIssueListView.as_view(), name='license_list'),
    path('<uuid:id>/license_detail/', LicenseDetailView.as_view(), name='license_detail'),
    path('<uuid:id>/issue_license/', IssueLicenseView.as_view(), name='issue_license'),
    path('license_issued/', LicensesListView.as_view(), name='license_issued'),
    path('<uuid:id>/generate_license/', GeneratePdfView.as_view(), name='generate_license'),
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),

   



]
