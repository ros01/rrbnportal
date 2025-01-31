from django.urls import path
from django.shortcuts import render
from . import views
from .views import (
    HospitalProfileListView,
    HospitalUploadListView,
    HospitalsUpdatedUploadListView,
    AllHospitalsView,
    HospitalProfileDetails,
    NewHospitalProfileDetails,
    UpdateHospitalProfileDetails,
    HospitalProfileCreateView,
    HospitalRegistrationDetails,
    HospitalPaymentDetails,
    HospitalVerificationDetails,
    HospitalScheduleDetails,
    HospitalInspectionDetails,
    HospitalAccreditationDetails,
    HospitalInspectionApprovalDetails,
    HospitalAccreditationApprovalDetails,
    HospitalInspectionRegistrarApprovalDetails,
    HospitalAccreditationRegistrarApprovalDetails,
    HospitalLicenseDetails,
    RegistrationListView,
    MyUserAccount,
    UploadInternshipList,
    InspectionScheduleListView,
    InspectionScheduleCreateView,
    ScheduledInspectionsListView,
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
    PermitRenewalDetails,
    AccreditationDetailView,
    IssueLicenseView,
    IssueRadCertPermitView,
    IssueRadPracticePermitView,
    IssueRadPracticePermitRenewal,
    IssueAccreditationView,
    LicenseIssuedDetailView,
    RegPermitCertDetailView,
    RadPracticePermitDetailView,
    AccreditationIssuedDetailView,
    #LicensesListView,
    RadRegCerttificateListView,
    RadPracticePermitListView,
    AccreditationCertificateListView,
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
    path('upload_internship_centers', views.upload_internship_centers, name='upload_internship_centers'),
    path('upload_internship_list', views.UploadInternshipList.as_view(), name='upload_internship_list'),
    path('clear_database', views.clear_database, name='clear_database'),
    path('create_hospital_profile',  HospitalProfileCreateView.as_view(), name='create_hospital_profile'),
    path('downloadfile', views.downloadfile, name='downloadfile'),
    path('hospitals_profile_list',  HospitalProfileListView.as_view(), name='hospitals_profile_list'),
    path('hospitals_upload_list',  HospitalUploadListView.as_view(), name='hospitals_upload_list'),
    path('hospitals_updated_upload_list',  HospitalsUpdatedUploadListView.as_view(), name='hospitals_updated_upload_list'),
    path('<uuid:pk>/new_hospital_profile_details/', NewHospitalProfileDetails.as_view(), name='new_hospital_profile_details'),
    path('<uuid:pk>/update_hospital_profile_details/', UpdateHospitalProfileDetails.as_view(), name='update_hospital_profile_details'),
    # path('basic-upload', views.BasicUploadView.as_view(), name='basic_upload'),
    path('my_user_account/', MyUserAccount.as_view(), name='my_user_account'),
    path('registration_list/', RegistrationListView.as_view(), name='registration_list'),
    path('all_hospitals_application_list/', AllHospitalsView.as_view(), name='all_hospitals_application_list'),
    path('<uuid:pk>/hospital_profile_details/', HospitalProfileDetails.as_view(), name='hospital_profile_details'),
    path('<uuid:pk>/hospital_registration_details/', HospitalRegistrationDetails.as_view(), name='hospital_registration_details'),
    path('<uuid:pk>/hospital_payment_details/', HospitalPaymentDetails.as_view(), name='hospital_payment_details'),
    path('<uuid:pk>/hospital_verification_details/', HospitalVerificationDetails.as_view(), name='hospital_verification_details'),
    path('<uuid:pk>/hospital_schedule_details/', HospitalScheduleDetails.as_view(), name='hospital_schedule_details'),
    path('<uuid:pk>/hospital_inspection_details/', HospitalInspectionDetails.as_view(), name='hospital_inspection_details'),
    path('<uuid:pk>/hospital_accreditation_details/', HospitalAccreditationDetails.as_view(), name='hospital_accreditation_details'),
    path('<uuid:pk>/hospital_inspection_approval_details/', HospitalInspectionApprovalDetails.as_view(), name='hospital_inspection_approval_details'),
    path('<uuid:pk>/hospital_accreditation_approval_details/', HospitalAccreditationApprovalDetails.as_view(), name='hospital_accreditation_approval_details'),
    path('<uuid:pk>/hospital_inspection_registrar_approval_details/', HospitalInspectionRegistrarApprovalDetails.as_view(), name='hospital_inspection_registrar_approval_details'),
    path('<uuid:pk>/hospital_accreditation_registrar_approval_details/', HospitalAccreditationRegistrarApprovalDetails.as_view(), name='hospital_accreditation_registrar_approval_details'),
    path('<uuid:pk>/hospital_license_details/', HospitalLicenseDetails.as_view(), name='hospital_license_details'),
    path('<uuid:id>/vet_application/', VetApplication.as_view(), name='vet_application'),
    #path('<uuid:id>', views.vet_application, name='vet_application'),
    path('<uuid:id>/approve/', views.approve, name='approve'),
    path('inspectors-by-zone/', views.get_inspectors_by_zone_htmx, name='get_inspectors_by_zone_htmx'),
    path('<uuid:id>/rejection_details/', views.rejection_details, name="rejection_details"),
    path('<uuid:id>/inspection_rejection_details/', views.inspection_rejection_details, name="inspection_rejection_details"),
    path('<uuid:id>/appraisal_rejection_details/', views.appraisal_rejection_details, name="appraisal_rejection_details"),
    path('<uuid:id>/reject_application/', views.reject_application, name='reject_application'),
    path('rad_cert_reg_list/', RadRegCerttificateListView.as_view(), name='rad_cert_reg_list'),
    path('rad_practice_permit_list/', RadPracticePermitListView.as_view(), name='rad_practice_permit_list'),
    path('accreditation_cert_list/', AccreditationCertificateListView.as_view(), name='accreditation_cert_list'),
    path('<uuid:id>/download_rad_cert_reg/', views.download_rad_cert_reg, name='download_rad_cert_reg'),
    path('<uuid:id>/download_rad_practice_permit/', views.download_rad_practice_permit, name='download_rad_practice_permit'),
    path('<uuid:id>/download_accreditation_cert/', views.download_accreditation_cert, name='download_accreditation_cert'),
    path('inspection_list/', InspectionScheduleListView.as_view(), name='inspection_list'),
    path('scheduled_inspections_list/', ScheduledInspectionsListView.as_view(), name='scheduled_inspections_list'),
    path('<uuid:pk>/inspection_schedule/', InspectionScheduleCreateView.as_view(), name='inspection_schedule'),
    path('<uuid:pk>/appraisal_schedule/', AppraisalCreateView.as_view(), name='appraisal_schedule'),
    path('<uuid:pk>/inspection_details/', InspectionCreateDetailView.as_view(), name='inspection_details'),
    path('inspections_list/', InspectionCompletedListView.as_view(), name='inspections_list'),
    path('<uuid:pk>/inspection_report/', InspectionCompletedDetailView.as_view(), name='inspection_report'),
    path('create_hospital_record/', RecordsCreateView.as_view(), name='create_hospital_record'),
    path('<uuid:id>/hospital_record_details/', RecordsDetailView.as_view(), name='hospital_record_details'),
    path('hospital_records_list/', HospitalRecordsListView.as_view(), name='hospital_records_list'),
    path('<uuid:id>/view_records/', HospitalRecordsDetailView.as_view(), name='view_records'),
    path('license_list/', LicenseIssueListView.as_view(), name='license_list'),
    path('<uuid:pk>/accreditation_report/', AccreditationCompletedDetailView.as_view(), name='accreditation_report'),
    path('<uuid:id>/approve_appraisal_report/', views.approve_appraisal_report, name='approve_appraisal_report'),
    path('<uuid:id>/reject_appraisal_report/', views.reject_appraisal_report, name='reject_appraisal_report'),
    path('<uuid:id>/approve_report/', views.approve_report, name='approve_report'),
    path('<uuid:id>/reject_report/', views.reject_report, name='reject_report'),
    path('license_list_table/', LicenseIssueListTable.as_view(), name='license_list_table'),
    path('accreditation_list_table/', AccreditationIssueListTable.as_view(), name='accreditation_list_table'),
    path('renewal_list_table/', RenewalIssueListTable.as_view(), name='renewal_list_table'),
    path('<uuid:id>/license_detail/', LicenseDetailView.as_view(), name='license_detail'),
    path('<uuid:id>/practice_permit_renewal_details/', PermitRenewalDetails.as_view(), name='practice_permit_renewal_details'),
    path('<uuid:id>/accreditation_detail/', AccreditationDetailView.as_view(), name='accreditation_detail'),
    #path('<uuid:pk>/issue_license/', IssueLicenseView.as_view(), name='issue_license'),
    path('<uuid:pk>/issue_reg_cert_permit/', IssueRadCertPermitView.as_view(), name='issue_reg_cert_permit'),
    path('<uuid:pk>/issue_rad_practice_permit/', IssueRadPracticePermitView.as_view(), name='issue_rad_practice_permit'),
    path('<uuid:pk>/issue_rad_practice_permit_renewal/', IssueRadPracticePermitRenewal.as_view(), name='issue_rad_practice_permit_renewal'),
    path('<uuid:pk>/issue_accreditation/', IssueAccreditationView.as_view(), name='issue_accreditation'),
    path('<uuid:id>/reg_permit_cert_details/', RegPermitCertDetailView.as_view(), name='reg_permit_cert_details'),
    path('<uuid:id>/rad_practice_permit_details/', RadPracticePermitDetailView.as_view(), name='rad_practice_permit_details'),
    path('<uuid:id>/issued_license_details/', LicenseIssuedDetailView.as_view(), name='issued_license_details'),
    path('<uuid:id>/issued_accreditation_details/', AccreditationIssuedDetailView.as_view(), name='issued_accreditation_details'),
    path('<uuid:id>/generate_license/', GeneratePdfView.as_view(), name='generate_license'),
    path('<uuid:id>/generate_license_pdf/', views.getPDF, name='generate_license_pdf'),
    #path('<uuid:id>/inspection_report/', views.inspection_report, name='inspection_report'),
    path('<uuid:id>/validate/', views.validate, name='validate'),
    #path('<uuid:id>/view_report/', views.view_report, name='view_report'),
    path('<uuid:id>/view_appraisal_report/', views.view_appraisal_report, name='view_appraisal_report'),
    path('<uuid:id>/issue_license/', IssueLicenseView.as_view(), name='issue_license'),
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),
]
