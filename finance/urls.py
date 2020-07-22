from django.urls import path

from . import views
from .views import (
    
    PaymentsListView,
    PaymentDetailView,
    RegisteredHospitalsListView,
    RegisterdHospitalsDetailView,
   
)

app_name = 'finance'

urlpatterns = [
    path('', views.index, name='finance_dashboard'),
    path('payments_list/', PaymentsListView.as_view(), name='payments_list'),
    path('<uuid:id>/payment_details/', PaymentDetailView.as_view(), name='payment_details'),
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),

]