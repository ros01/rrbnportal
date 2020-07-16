from django.urls import path

from . import views
from .views import (
    EnuguScheduleListView,
    LagosScheduleListView,
    InspectionView,
    InspectionReportView,
    AbujaScheduleListView,
    DashboardTemplateView,
)

from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView,
     TemplateView
)



app_name = 'zonal_offices'

urlpatterns = [
   
    path('', DashboardTemplateView.as_view(), name='zonal_offices_dashboard'),
    path('offices', views.offices, name='rrbn_offices'),
    path('enugu_list/', EnuguScheduleListView.as_view(), name='enugu_list'),
    path('lagos_list/', LagosScheduleListView.as_view(), name='lagos_list'),
    path('abuja_list/', AbujaScheduleListView.as_view(), name='abuja_list'),
    path('<uuid:id>/inspection_detail/', InspectionView.as_view(), name='inspection_detail'),
    path('<uuid:id>/inspection_report/', InspectionReportView.as_view(), name='inspection_report'),

]
