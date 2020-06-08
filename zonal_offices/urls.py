from django.urls import path

from . import views
from .views import (
    InspectionScheduleListView,
    InspectionView,
    InspectionReportView,
)



app_name = 'zonal_offices'

urlpatterns = [
    path('', views.index, name='zonal_offices_dashboard'),
    path('offices', views.offices, name='rrbn_offices'),
    path('inspection_list/', InspectionScheduleListView.as_view(), name='inspection_list'),
    path('<int:id>/inspection_detail/', InspectionView.as_view(), name='inspection_detail'),
    path('<int:id>/inspection_report/', InspectionReportView.as_view(), name='inspection_report'),

]
