from django.urls import path
from django.shortcuts import render
from . import views

from .views import (
    StartNewRadApplication,
    StartGovInternshipApplication,
    StartApplication,
    RegisterFacility,  
    HospitalDetailView,
    FacilityDetailView,
    PaymentListView,
    GenerateInvoiceView,
    PaymentCreateView,
    PaymentDetailView,
    PaymentProcessing,
    PaymentVerificationsView,
    PaymentConfirmation,
    PaymentVerificationListView,
    VerificationsSuccessfulView,
    ScheduleListView,
    ScheduleDetailView,
    InspectionListView,
    InspectionView,
    AppraisalView,
    InspectionApprovedView,
    AccreditationInspectionApprovedView,
    MyLicensesListView,
    MyLicensesDetailView,
    DownloadLicense,
    MyApplicationListView,
    MyAccreditationlListView,
    MyLicenseApplicationsHistory,
    LicenseIssuanceView,
    InternshipLicenseIssuanceView,
    StartLicenseRenewal,
    StartNewApplication,
    HospitalRenewView,
)



app_name = 'hospitals'


urlpatterns = [
    path('', views.hospitals_dashboard, name='hospitals_dashboard'),
    path('status/', views.status, name='status'),
    path('application_list/', MyApplicationListView.as_view(), name='application_list'),
    path('<uuid:pk>/start_new_radiography_license_application/', StartNewRadApplication.as_view(), name='start_new_radiography_license_application'),
    path('<uuid:pk>/start_gov_internship_accreditation_application/', StartGovInternshipApplication.as_view(), name='start_gov_internship_accreditation_application'),
    path('<uuid:pk>/start_application/', StartApplication.as_view(), name='start_application'),
    path('start_new_application/', StartNewApplication.as_view(), name='start_new_application'),
    path('<uuid:id>/hospital_details/', HospitalDetailView.as_view(), name='hospital_details'),
    path('<uuid:id>/facility_details/', FacilityDetailView.as_view(), name='facility_details'),
    path('<uuid:pk>/generate_invoice/', GenerateInvoiceView.as_view(), name='generate_invoice'),
    path('payment_table/', PaymentListView.as_view(), name='payment_table'),
    path('<uuid:pk>/payment_processing/', PaymentCreateView.as_view(), name='payment_processing'),
    path('<uuid:pk>/payment_transaction/', PaymentProcessing.as_view(), name='payment_transaction'),
    path('<uuid:id>/payment_details/', PaymentDetailView.as_view(), name='payment_details'),
    path('<uuid:pk>/payment_verifications/', PaymentVerificationsView.as_view(), name='payment_verifications'),
    path('<uuid:pk>/verifications_successful/', VerificationsSuccessfulView.as_view(), name='verifications_successful'),
    path('<uuid:pk>/schedule_detail/', ScheduleDetailView.as_view(), name='schedule_detail'),
    path('<uuid:pk>/inspection_processing/', InspectionView.as_view(), name='inspection_processing'),
    path('<uuid:id>/inspection_passed/', InspectionApprovedView.as_view(), name='inspection_passed'),
    path('<uuid:id>/appraisal_passed/', AccreditationInspectionApprovedView.as_view(), name='appraisal_passed'),
    path('<uuid:pk>/license_issuance/', LicenseIssuanceView.as_view(), name='license_issuance'),
    path('<uuid:pk>/internship_license_issuance/', InternshipLicenseIssuanceView.as_view(), name='internship_license_issuance'),
    path('<uuid:pk>/license_details/', MyLicensesDetailView.as_view(), name='license_details'),
    path('license_history/', MyLicenseApplicationsHistory.as_view(), name='license_history'),
    path('accreditation_list/', MyAccreditationlListView.as_view(), name='accreditation_list'),
    path('<uuid:id>/start_renewal/', StartLicenseRenewal.as_view(), name='start_renewal'),
    path('hospital_renewal/', HospitalRenewView.as_view(), name='hospital_renewal'),
    path('start_registration/', RegisterFacility.as_view(), name='start_registration'),
    
    
    path('<uuid:id>/payment_confirmation/', PaymentConfirmation.as_view(), name='payment_confirmation'),
    
    path('payment_verified_table/', PaymentVerificationListView.as_view(), name='payment_verified_table'),
    
    path('schedule_table/', ScheduleListView.as_view(), name='schedule_table'),
    path('inspection_table/', InspectionListView.as_view(), name='inspection_table'),
    
    path('<uuid:id>/appraisal_processing/', AppraisalView.as_view(), name='appraisal_processing'),
    
    
    
    
    path('licenses_list/', MyLicensesListView.as_view(), name='licenses_list'),
    
    path('<uuid:id>/license_download/', DownloadLicense.as_view(), name='license_download'),
    path('lookup/', views.lookup, name='hospitals_lookup'),
    #path('start_application/<uuid:id>/', views.StartApplication, name="start_application"), 
    
]
