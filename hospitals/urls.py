from django.urls import path
from django.shortcuts import render
from . import views
from .views import (
    HospitalCreateView,
    HospitalUpdateView,
    PaymentListView,
    PaymentCreateView,
    PaymentUpdateView,
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
    #path('<int:id>/payment_table/', views.payment_table, name='payment_table'),
    #path('payment_table', views.payment_table, name='payment_table'),

    #path('<int:id>/', views.payment_table, name='payment_table'),
    #path('payment_table', views.payment_table, name='payment_table'),
    path('inspection_table/', InspectionListView.as_view(), name='inspection_table'),
    path('payment_table/', PaymentListView.as_view(), name='payment_table'),
    #path('inspection_table', views.inspection_table, name='inspection_table'),
    #path('license_table', views.license_table, name='license_table'),
    path('register/', HospitalCreateView.as_view(), name='hospitals_register'),
    path('<int:id>/payment_processing/', PaymentCreateView.as_view(), name='payment_processing'),
    path('<int:id>/inspection_processing/', InspectionView.as_view(), name='inspection_processing'),
    #path('<int:id>', views.registration, name='registration'),
    
    #path('payment_details', views.payment_details, name='payment_details'),
    path('<int:id>/payment_update/', PaymentUpdateView.as_view(), name='payment_update'),
    path('<int:id>/update/', HospitalUpdateView.as_view(), name='update'),
    path('lookup/', views.lookup, name='hospitals_lookup'),
    path('licenses_list/', MyLicensesListView.as_view(), name='licenses_list'),
    path('<int:id>/licenses_detail/', MyLicensesDetailView.as_view(), name='licenses_detail'),



]
