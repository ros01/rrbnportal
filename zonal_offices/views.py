from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import zonaloffices_required
from hospitals.models import Schedule, Inspection
from .forms import InspectionModelForm
from django.views import View
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView
)
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import send_mail

@login_required
@zonaloffices_required
def index(request):
    return render (request, 'zonal_offices/zonal_offices_dashboard.html')

@login_required
def offices(request):
  return render(request, 'zonal_offices/rrbn_offices.html')


class InspectionScheduleListView(View):
    template_name = "zonal_offices/inspection_schedule_list.html"
    queryset = Schedule.objects.all()

    def get_queryset(self):
        return self.queryset.filter(inspection_zone="Enugu")
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class InspectionObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionView(InspectionObjectMixin, View):
    template_name = "zonal_offices/inspection_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


#class InspectionCreateView(CreateView):
    #template_name = 'zonal_offices/inspection_report_creation.html'
    #form_class =InspectionModelForm
    #queryset = Schedule.objects.all()


class InspectionReportView(InspectionObjectMixin, View):
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
           #to_email = [request.user.email]
           to_email = [form.cleaned_data.get('email')]

           context['form'] = form
           contact_message = get_template(
               'zonal_offices/inspection_report.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        
        
        return render(request, self.template_name1, context)
