from django.urls import path

from . import views



app_name = 'zonal_offices'

urlpatterns = [
    path('', views.index, name='zonal_offices_dashboard'),
    path('offices', views.offices, name='rrbn_offices'),

]
