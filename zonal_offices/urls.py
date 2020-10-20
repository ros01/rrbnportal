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
    UltrasoundScore,
    UltrasoundScoreUpdate,
    UltrasoundScoreDetail,
    NuclearMedicineScore,
    NuclearMedicineScoreDetail,
    NuclearMedicineScoreUpdate,
    RadiotherapyScore,
    RadiotherapyScoreUpdate,
    MriScore,
    MriScoreUpdate,
    CtscanScore,
    CtscanScoreUpdate,
    XrayScore,
    XrayScoreUpdate,
    XrayScoreDetail,
    FlouroscopyScore,
    FlouroscopyScoreUpdate,
    MamographyScore,
    MamographyScoreUpdate, 
    DentalXrayScore,
    DentalXrayScoreUpdate,
    EchocardiographyScore,
    EchocardiographyScoreUpdate,
    AngiographyScore,
    AngiographyScoreUpdate,
    CarmScore,
    CarmScoreUpdate,
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
    path('inspection_reports_list/', InspectionReportsView.as_view(), name='inspection_reports_list'),
    path('<uuid:id>/view_inspection_report/', views.view_inspection_report, name='view_inspection_report'),
    path('<uuid:id>/ultrasound_score/', UltrasoundScore.as_view(), name='ultrasound_score'),
    path('<uuid:id>/ultrasound_detail/', UltrasoundScoreDetail.as_view(), name='ultrasound_detail'),
    path('<uuid:id>/ultrasound_update/', UltrasoundScoreUpdate.as_view(), name='ultrasound_update'),
    path('<uuid:id>/nuclear_medicine_score/', NuclearMedicineScore.as_view(), name='nuclear_medicine_score'),
    path('<uuid:id>/nuclear_medicine_detail/', NuclearMedicineScoreDetail.as_view(), name='nuclear_medicine_detail'),
    path('<uuid:id>/nuclear_medicine_update/', NuclearMedicineScoreUpdate.as_view(), name='nuclear_medicine_update'),
    path('<uuid:id>/radiotherapy_score/', RadiotherapyScore.as_view(), name='radiotherapy_score'),
    path('<uuid:id>/radiotherapy_update/', RadiotherapyScoreUpdate.as_view(), name='radiotherapy_update'),
    path('<uuid:id>/mri_score/', MriScore.as_view(), name='mri_score'),
    path('<uuid:id>/mri_update/', MriScoreUpdate.as_view(), name='mri_update'),
    path('<uuid:id>/ctscan_score/', CtscanScore.as_view(), name='ctscan_score'),
    path('<uuid:id>/ctscan_update/', CtscanScoreUpdate.as_view(), name='ctscan_update'),
    path('<uuid:id>/xray_score/', XrayScore.as_view(), name='xray_score'),
    path('<uuid:id>/xray_detail/', XrayScoreDetail.as_view(), name='xray_detail'),
    path('<uuid:id>/xray_update/', XrayScoreUpdate.as_view(), name='xray_update'),
    path('<uuid:id>/flouroscopy_score/', FlouroscopyScore.as_view(), name='flouroscopy_score'),
    path('<uuid:id>/flouroscopy_update/', FlouroscopyScoreUpdate.as_view(), name='flouroscopy_update'),
    path('<uuid:id>/mamography_score/', MamographyScore.as_view(), name='mamography_score'),
    path('<uuid:id>/mamography_update/', MamographyScoreUpdate.as_view(), name='mamography_update'),
    path('<uuid:id>/dental_xray_score/', DentalXrayScore.as_view(), name='dental_xray_score'),
    path('<uuid:id>/dental_xray_update/', DentalXrayScoreUpdate.as_view(), name='dental_xray_update'),
    path('<uuid:id>/echocardiography_score/', EchocardiographyScore.as_view(), name='echocardiography_score'),
    path('<uuid:id>/echocardiography_update/', EchocardiographyScoreUpdate.as_view(), name='echocardiography_update'),
    path('<uuid:id>/angiography_score/', AngiographyScore.as_view(), name='angiography_score'),
    path('<uuid:id>/angiography_update/', AngiographyScoreUpdate.as_view(), name='angiography_update'),
    path('<uuid:id>/carm_score/', CarmScore.as_view(), name='carm_score'),
    path('<uuid:id>/carm_update/', CarmScoreUpdate.as_view(), name='carm_update'),
    path('<uuid:id>/accreditation_report/', AccreditationReportView.as_view(), name='accreditation_report'),
    path('hospitals_lookup/', RegisteredHospitalsListView.as_view(), name='hospitals_lookup'),
    path('<uuid:id>/hospital_details/', RegisterdHospitalsDetailView.as_view(), name='hospital_details'),
    path('create_hospital_record/', RecordsCreate.as_view(), name='create_hospital_record'),
    path('<uuid:id>/hospital_record_details/', RecordsDetail.as_view(), name='hospital_record_details'),
    path('hospital_records_list/', HospitalRecordsList.as_view(), name='hospital_records_list'),
    path('<uuid:id>/view_records/', HospitalRecordsDetail.as_view(), name='view_records'),

]
