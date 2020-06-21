from django.urls import path

from . import views
from .views import (
    
    PaymentsListView,
    PaymentDetailView,
   
)

app_name = 'finance'

urlpatterns = [
    path('', views.index, name='finance_dashboard'),
    path('payments_list/', PaymentsListView.as_view(), name='payments_list'),
    path('<int:id>/payment_details/', PaymentDetailView.as_view(), name='payment_details'),

]