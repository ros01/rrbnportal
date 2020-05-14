from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('get_object_or_404', views.get_object_or_404, name='404'),
    path('contact', views.contact, name='contact'),
    path('mission', views.mission, name='mission'),
    path('mandate', views.mandate, name='mandate'),
    path('benefits', views.benefits, name='benefits'),
    path('faq', views.faq, name='faq'),
    path('guidelines', views.guidelines, name='guidelines'),
    path('internship_centers', views.internship_centers, name='internship_centers'),
    path('zonal_offices', views.zonal_offices, name='zonal_offices'),
    
    ]