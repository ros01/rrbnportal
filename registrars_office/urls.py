from django.urls import path

from . import views

app_name = 'registrars_office'

urlpatterns = [
    path('', views.index, name='registrar_dashboard'),

]
