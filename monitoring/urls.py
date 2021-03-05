from django.urls import path
from django.shortcuts import render
from . import views
from .views import (
    
    RegistrationListView,
    InspectionScheduleListView,
    InspectionCreateView,
    AppraisalCreateView,
    InspectionCreateDetailView,
    InspectionCompletedListView,
    InspectionCompletedDetailView,
    AccreditationCompletedDetailView,
    LicenseIssueListView,
    LicenseIssueListTable,
    AccreditationIssueListTable,
    RenewalIssueListTable,
    LicenseDetailView,
    AccreditationDetailView,
    IssueLicenseView,
    IssueAccreditationView,
    LicenseIssuedDetailView,
    AccreditationIssuedDetailView,
    LicensesListView,
    GeneratePdfView,
    RegisteredHospitalsListView,
    RegisterdHospitalsDetailView,
    RecordsCreateView,
    RecordsDetailView,
    HospitalRecordsListView,
    HospitalRecordsDetailView, 
    VetApplication,  
)

# Create your views here.


app_name = 'monitoring'


urlpatterns = [
    path('', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('registration_list/', RegistrationListView.as_view(), name='registration_list'),
    path('<uuid:id>/vet_application/', VetApplication.as_view(), name='vet_application'),
    #path('<uuid:id>', views.vet_application, name='vet_application'),
    path('<uuid:id>/approve/', views.approve, name='approve'),
    path('<uuid:id>/reject/', views.reject, name='reject'),
    path('inspection_list/', InspectionScheduleListView.as_view(), name='inspection_list'),
    path('<uuid:pk>/inspection_schedule/', InspectionCreateView.as_view(), name='inspection_schedule'),
    path('<uuid:pk>/appraisal_schedule/', AppraisalCreateView.as_view(), name='appraisal_schedule'),
    path('create_hospital_record/', RecordsCreateView.as_view(), name='create_hospital_record'),
    path('<uuid:id>/hospital_record_details/', RecordsDetailView.as_view(), name='hospital_record_details'),
    path('hospital_records_list/', HospitalRecordsListView.as_view(), name='hospital_records_list'),
    path('<uuid:id>/view_records/', HospitalRecordsDetailView.as_view(), name='view_records'),
    path('<uuid:id>/inspection_details/', InspectionCreateDetailView.as_view(), name='inspection_details'),
    path('inspections_list/', InspectionCompletedListView.as_view(), name='inspections_list'),
    path('<uuid:id>/inspection_report/', InspectionCompletedDetailView.as_view(), name='inspection_report'),
    path('license_list/', LicenseIssueListView.as_view(), name='license_list'),
    path('<uuid:id>/accreditation_report/', AccreditationCompletedDetailView.as_view(), name='accreditation_report'),
    path('<uuid:id>/approve_appraisal_report/', views.approve_appraisal_report, name='approve_appraisal_report'),
    path('<uuid:id>/reject_appraisal_report/', views.reject_appraisal_report, name='reject_appraisal_report'),
    path('<uuid:id>/approve_report/', views.approve_report, name='approve_report'),
    path('<uuid:id>/reject_report/', views.reject_report, name='reject_report'),
    path('license_list_table/', LicenseIssueListTable.as_view(), name='license_list_table'),
    path('accreditation_list_table/', AccreditationIssueListTable.as_view(), name='accreditation_list_table'),
    path('renewal_list_table/', RenewalIssueListTable.as_view(), name='renewal_list_table'),
    path('<uuid:id>/license_detail/', LicenseDetailView.as_view(), name='license_detail'),
    path('<uuid:id>/accreditation_detail/', AccreditationDetailView.as_view(), name='accreditation_detail'),
    path('<uuid:pk>/issue_license/', IssueLicenseView.as_view(), name='issue_license'),
    path('<uuid:pk>/issue_accreditation/', IssueAccreditationView.as_view(), name='issue_accreditation'),
    path('<uuid:id>/issued_license_details/', LicenseIssuedDetailView.as_view(), name='issued_license_details'),
    path('<uuid:id>/issued_accreditation_details/', AccreditationIssuedDetailView.as_view(), name='issued_accreditation_details'),
    path('license_issued/', LicensesListView.as_view(), name='license_issued'),
    path('<uuid:id>/generate_license/', GeneratePdfView.as_view(), name='generate_license'),
    
    #path('<uuid:id>/inspection_report/', views.inspection_report, name='inspection_report'),
    path('<uuid:id>/validate/', views.validate, name='validate'),
    #path('<uuid:id>/view_report/', views.view_report, name='view_report'),
    path('<uuid:id>/view_appraisal_report/', views.view_appraisal_report, name='view_appraisal_report'),
    
    
    
    
    
    path('<uuid:id>/issue_license/', IssueLicenseView.as_view(), name='issue_license'),
    
    
    
    
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),
]
