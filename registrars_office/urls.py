from django.urls import path
from django.shortcuts import render

from . import views
from .views import (
    LicenseApprovalListView,
    MyUserAccount,
    InternshipCertificateList,
    NewPracticePermitList,
    PracticePermitRenewalList,
    LicenseApprovalDetailView,
    PracticePermitRenewalAppDetails,
    InternshipLicenseApprovalDetailView,
    IssuedLicensesListView,
    LicensePdfView,
    InspectionCompletedListView,
    InspectionCompletedDetailView,
    AccreditationCompletedDetailView,
    RegisteredHospitalsListView,
    RegisterdHospitalsDetailView,
    RadRegCerttificateListView,
    RadPracticePermitListView,
    AccreditationCertificateListView,


)

app_name = 'registrars_office'

urlpatterns = [
    path('', views.index, name='registrar_dashboard'),
    path('my_user_account/', MyUserAccount.as_view(), name='my_user_account'),
    path('license_approval_list/', LicenseApprovalListView.as_view(), name='license_approval_list'),
    path('internship_certificate_list/', InternshipCertificateList.as_view(), name='internship_certificate_list'),
    path('new_practice_permit_list/', NewPracticePermitList.as_view(), name='new_practice_permit_list'),
    path('practice_permit_renewal_list/', PracticePermitRenewalList.as_view(), name='practice_permit_renewal_list'),
    path('<uuid:id>/license_approval_details/', LicenseApprovalDetailView.as_view(), name='license_approval_details'),
    path('<uuid:id>/practice_permit_renewal_app_details/', PracticePermitRenewalAppDetails.as_view(), name='practice_permit_renewal_app_details'),
    path('<uuid:id>/internship_license_approval_details/', InternshipLicenseApprovalDetailView.as_view(), name='internship_license_approval_details'),
    path('<uuid:id>/validate/', views.validate, name='validate'),
    path('<uuid:id>/validate_report/', views.validate_report, name='validate_report'),
    path('inspection_reports_list/', InspectionCompletedListView.as_view(), name='inspection_reports_list'),
    path('<uuid:id>/inspection_report/', InspectionCompletedDetailView.as_view(), name='inspection_report'),
    path('<uuid:id>/accreditation_report/', AccreditationCompletedDetailView.as_view(), name='accreditation_report'),
    path('<uuid:id>/view_inspection_report/', views.view_inspection_report, name='view_inspection_report'),
    path('<uuid:id>/view_appraisal_report/', views.view_appraisal_report, name='view_appraisal_report'),
    path('<uuid:id>/approve_license/', views.approve_license, name='approve_license'),
    path('<uuid:id>/approve_practice_permit_renewal/', views.approve_practice_permit_renewal, name='approve_practice_permit_renewal'),
    path('<uuid:id>/reject_license/', views.reject_license, name='reject_license'),
    path('<uuid:id>/approve_internship_license/', views.approve_internship_license, name='approve_internship_license'),
    path('<uuid:id>/reject_internship_license/', views.reject_internship_license, name='reject_internship_license'),
    path('issued_lisenses_list/', IssuedLicensesListView.as_view(), name='issued_lisenses_list'),
    path('rad_cert_reg_list/', RadRegCerttificateListView.as_view(), name='rad_cert_reg_list'),
    path('rad_practice_permit_list/', RadPracticePermitListView.as_view(), name='rad_practice_permit_list'),
    path('accreditation_cert_list/', AccreditationCertificateListView.as_view(), name='accreditation_cert_list'),
    path('<uuid:id>/download_rad_cert_reg/', views.download_rad_cert_reg, name='download_rad_cert_reg'),
    path('<uuid:id>/download_rad_practice_permit/', views.download_rad_practice_permit, name='download_rad_practice_permit'),
    path('<uuid:id>/download_accreditation_cert/', views.download_accreditation_cert, name='download_accreditation_cert'),
    path('<uuid:id>/generate_pdf/', LicensePdfView.as_view(), name='generate_pdf'),
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),
    

]
