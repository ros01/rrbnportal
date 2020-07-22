from django.urls import path

from . import views
from .views import (
    EnuguScheduleListView,
    LagosScheduleListView,
    InspectionView,
    InspectionReportView,
    AccreditationReportView,
    AbujaScheduleListView,
    DashboardTemplateView,
    InspectionReportsView,
    RegisteredHospitalsListView,
    RegisterdHospitalsDetailView,
    RecordsCreate,
    RecordsDetail,
    HospitalRecordsList,
    HospitalRecordsDetail,
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
    path('<uuid:id>/accreditation_report/', AccreditationReportView.as_view(), name='accreditation_report'),
    path('inspection_reports_list/', InspectionReportsView.as_view(), name='inspection_reports_list'),
    path('<uuid:id>/view_inspection_report/', views.view_inspection_report, name='view_inspection_report'),
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),
    path('create_hospital_record/', RecordsCreate.as_view(), name='create_hospital_record'),
    path('<uuid:id>/hospital_record_details/', RecordsDetail.as_view(), name='hospital_record_details'),
    path('hospital_records_list/', HospitalRecordsList.as_view(), name='hospital_records_list'),
    path('<uuid:id>/view_records/', HospitalRecordsDetail.as_view(), name='view_records'),

]
