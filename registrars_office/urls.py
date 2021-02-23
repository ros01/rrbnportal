from django.urls import path
from django.shortcuts import render

from . import views
from .views import (
    LicenseApprovalListView,
    LicenseApprovalDetailView,
    IssuedLicensesListView,
    LicensePdfView,
    InspectionReportsView,
    RegisteredHospitalsListView,
    RegisterdHospitalsDetailView,
)

app_name = 'registrars_office'

urlpatterns = [
    path('', views.index, name='registrar_dashboard'),
    path('license_approval_list/', LicenseApprovalListView.as_view(), name='license_approval_list'),
    path('<uuid:id>/license_approval_details/', LicenseApprovalDetailView.as_view(), name='license_approval_details'),
    path('<uuid:id>/validate/', views.validate, name='validate'),
    path('<uuid:id>/validate_report/', views.validate_report, name='validate_report'),
    path('inspection_reports_list/', InspectionReportsView.as_view(), name='inspection_reports_list'),
    path('<uuid:id>/view_inspection_report/', views.view_inspection_report, name='view_inspection_report'),
    path('<uuid:id>/view_appraisal_report/', views.view_appraisal_report, name='view_appraisal_report'),
    path('<uuid:id>/approve_license/', views.approve_license, name='approve_license'),
    path('<uuid:id>/reject_license/', views.reject_license, name='reject_license'),
    path('<uuid:id>/approve_internship_license/', views.approve_internship_license, name='approve_internship_license'),
    path('<uuid:id>/reject_internship_license/', views.reject_internship_license, name='reject_internship_license'),
    path('issued_lisenses_list/', IssuedLicensesListView.as_view(), name='issued_lisenses_list'),
    path('<uuid:id>/generate_pdf/', LicensePdfView.as_view(), name='generate_pdf'),
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),
    

]
