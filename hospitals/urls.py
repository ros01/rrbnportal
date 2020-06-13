from django.urls import path
from django.shortcuts import render
from . import views
from .views import (
    HospitalCreateView,
    HospitalUpdateView,
    PaymentListView,
    PaymentCreateView,
    PaymentUpdateView,
    PaymentVerificationListView,
    PaymentVerificationDetailView,
    ScheduleListView,
    ScheduleDetailView,
    InspectionListView,
    InspectionView,
    MyLicensesListView,
    MyLicensesDetailView,

)



app_name = 'hospitals'


urlpatterns = [
    path('', views.hospitals_dashboard, name='hospitals_dashboard'),
    path('status/', views.status, name='status'),
    path('reg_table', views.reg_table, name='reg_table'),
    path('register/', HospitalCreateView.as_view(), name='hospitals_register'),
    path('<int:id>/update/', HospitalUpdateView.as_view(), name='update'),
    path('payment_table/', PaymentListView.as_view(), name='payment_table'),
    path('<int:id>/payment_processing/', PaymentCreateView.as_view(), name='payment_processing'),
    path('<int:id>/payment_update/', PaymentUpdateView.as_view(), name='payment_update'),
    path('payment_verified_table/', PaymentVerificationListView.as_view(), name='payment_verified_table'),
    path('<int:id>/payment_detail/', PaymentVerificationDetailView.as_view(), name='payment_detail'),
    path('schedule_table/', ScheduleListView.as_view(), name='schedule_table'),
    path('<int:id>/schedule_detail/', ScheduleDetailView.as_view(), name='schedule_detail'),
    path('inspection_table/', InspectionListView.as_view(), name='inspection_table'),
    path('<int:id>/inspection_processing/', InspectionView.as_view(), name='inspection_processing'),
    path('licenses_list/', MyLicensesListView.as_view(), name='licenses_list'),
    path('<int:id>/license_details/', MyLicensesDetailView.as_view(), name='license_details'),
    path('lookup/', views.lookup, name='hospitals_lookup'),
    
]
