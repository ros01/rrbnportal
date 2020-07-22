from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import zonaloffices_required
from hospitals.models import Schedule, Inspection, License, Records
from .forms import InspectionModelForm, RecordsModelForm, AccreditationModelForm
from django.views import View
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView,
     TemplateView
)
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy


class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)




class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "zonal_offices/zonal_offices_dashboard.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(DashboardTemplateView, self).get_context_data(*args, **kwargs)
        context["inspection"] = Schedule.objects.all()
        return context


class EnuguScheduleListView(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/enugu_schedule_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.all().filter(inspection_zone="Enugu")
        

    def get_context_data(self, **kwargs):
        obj = super(EnuguScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Enugu")
        obj['inspection_qs'] = Inspection.objects.filter(application_status=4)
        return obj


class LagosScheduleListView(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/lagos_schedule_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.all().filter(inspection_zone="Lagos")
        

    def get_context_data(self, **kwargs):
        obj = super(LagosScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Lagos")
        obj['inspection_qs'] = Inspection.objects.filter(application_status=4)
        return obj

class AbujaScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'zonal_offices/abuja_schedule_list.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Schedule.objects.all().filter(inspection_zone="Abuja")


    def get_context_data(self, **kwargs):
        obj = super(AbujaScheduleListView, self).get_context_data(**kwargs)
        obj['schedule_qs'] = Schedule.objects.filter(inspection_zone="Abuja")
        obj['inspection_qs'] = Inspection.objects.filter(application_status=4)
        return obj
        

class InspectionObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "zonal_offices/inspection_detail.html" 
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class InspectionReportView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "zonal_offices/inspection_report_creation.html"
    template_name1 = "zonal_offices/inspection_report_confirmation.html"
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = InspectionModelForm(instance=obj)  
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)


    def post(self, request,  *args, **kwargs):
        form = InspectionModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form

           subject = 'Notice of Facility Inspection'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [form.cleaned_data.get('email')]

           context['form'] = form
           contact_message = get_template(
               'zonal_offices/inspection_report.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        
        
        return render(request, self.template_name1, context)


class AccreditationReportView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "zonal_offices/accreditation_report_creation.html"
    template_name1 = "zonal_offices/accreditation_report_confirmation.html"
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AccreditationModelForm(instance=obj)  
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)


    def post(self, request,  *args, **kwargs):
        form = AccreditationModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form

           subject = 'Notice of Facility Inspection'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [form.cleaned_data.get('email')]

           context['form'] = form
           contact_message = get_template(
               'zonal_offices/accreditation_report.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        
        
        return render(request, self.template_name1, context)

class InspectionReportsView(LoginRequiredMixin, View):
    template_name = "zonal_offices/inspection_reports_list.html"
    queryset = Inspection.objects.all()

    def get_queryset(self):
        return self.queryset
        #return self.queryset
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)



def view_inspection_report(request, id):
  inspection = get_object_or_404(Inspection, pk=id)
  
  context={'inspection': inspection,
           
           }
  return render(request, 'zonal_offices/inspection_details.html', context)



class RecordsCreate(LoginRequiredMixin, CreateView):
    template_name = 'zonal_offices/create_hospital_records.html'

    form_class = RecordsModelForm

    def get_success_url(self):
        return reverse('zonal_offices:hospital_record_details', kwargs={'id' : self.object.id})

   
    


class RecordsObjectMixin(object):
    model = Records
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class RecordsDetail(LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "zonal_offices/hospitals_records_confirmation.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)



class HospitalRecordsList(LoginRequiredMixin, ListView):
    template_name = "zonal_offices/hospital_records_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Records.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(HospitalRecordsList, self).get_context_data(**kwargs)
        obj['records_qs'] = Records.objects.order_by('-date_visited')
        return obj
        



class HospitalRecordsDetail(LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "zonal_offices/hospital_records_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)








class RegisteredHospitalsListView(LoginRequiredMixin, View):
    template_name = "zonal_offices/registered_hospitals_list.html"
    queryset = License.objects.all()

    def get_queryset(self):
        return self.queryset
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


class RegisteredObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class RegisterdHospitalsDetailView(LoginRequiredMixin, RegisteredObjectMixin, View):
    template_name = "zonal_offices/hospital_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)





@login_required
def offices(request):
  return render(request, 'zonal_offices/rrbn_offices.html')
