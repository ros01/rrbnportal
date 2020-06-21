from django.urls import path
from django.shortcuts import render

from . import views
from .views import (
    LicenseApprovalListView,
    IssuedLicensesListView,
    LicensePdfView,
)

app_name = 'registrars_office'

urlpatterns = [
    path('', views.index, name='registrar_dashboard'),
    path('license_approval_list/', LicenseApprovalListView.as_view(), name='license_approval_list'),
    path('<int:id>/validate/', views.validate, name='validate'),
    path('<int:id>/approve_license/', views.approve_license, name='approve_license'),
    path('<int:id>/reject_license/', views.reject_license, name='reject_license'),
    path('issued_lisenses_list/', IssuedLicensesListView.as_view(), name='issued_lisenses_list'),
    path('<int:id>/generate_pdf/', LicensePdfView.as_view(), name='generate_pdf'),

]
