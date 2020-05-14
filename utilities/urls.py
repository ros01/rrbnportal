from django.urls import path, include

from . import views



app_name = 'utilities'
urlpatterns = [
    path('offices', views.offices, name='offices'),
]
