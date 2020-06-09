from django.urls import path
from django.shortcuts import render
from . import views
from .views import (
    InspectionCreateView,
    RegistrationListView,
    InspectionScheduleListView,
    InspectionCompletedListView,
    LicenseIssueListView,
    LicenseDetailView,
    IssueLicenseView,
    LicensesListView,
    LicensesDetailView,
   
)

# Create your views here.


app_name = 'monitoring'


urlpatterns = [
    path('', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('<int:id>', views.vet_application, name='vet_application'),
    path('<int:id>/approve/', views.approve, name='approve'),
    path('<int:id>/reject/', views.reject, name='reject'),
    path('registration_list/', RegistrationListView.as_view(), name='registration_list'),
    path('inspection_list/', InspectionScheduleListView.as_view(), name='inspection_list'),
    path('<int:id>/inspection_schedule/', InspectionCreateView.as_view(), name='inspection_schedule'),
    path('inspections_list/', InspectionCompletedListView.as_view(), name='inspections_list'),
    #path('<int:id>/inspections_detail/', InspectionsDetailView.as_view(), name='inspections_detail'),
    path('<int:id>/verify/', views.verify, name='verify'),
    path('<int:id>/approve_report/', views.approve_report, name='approve_report'),
    path('<int:id>/reject_report/', views.reject_report, name='reject_report'),
    path('license_list/', LicenseIssueListView.as_view(), name='license_list'),
    path('<int:id>/license_detail/', LicenseDetailView.as_view(), name='license_detail'),
    path('<int:id>/issue_license/', IssueLicenseView.as_view(), name='issue_license'),
    path('license_issued/', LicensesListView.as_view(), name='license_issued'),
    path('<int:pk>/view_license/', LicensesDetailView.as_view(), name='view_license'),
   



]
