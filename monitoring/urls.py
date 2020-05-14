from django.urls import path
from django.shortcuts import render
from . import views
#from .views import (
    #PaymentsView,
    #RegVerifyView,
#)

# Create your views here.


app_name = 'monitoring'


urlpatterns = [
    path('', views.monitoring_dashboard, name='monitoring_dashboard'),
    #path('list', views.list, name='list'),
    path('<int:id>', views.vet_application, name='vet_application'),
    path('<int:id>/approve/', views.approve, name='approve'),
    path('<int:id>/reject/', views.reject, name='reject'),
    #path('<int:id>/vet_application/', RegVerifyView.as_view(), name='vet_application'),
    #path('registration_list/', PaymentsView.as_view(), name='registration_list'),
    path('registration_list/', views.registration_list, name='registration_list'),



]
