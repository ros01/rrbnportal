from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from accounts.decorators import monitoring_required
from hospitals.models import Payment, Registration, Schedule, Inspection, License
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.views import View
from . import views
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView
)
from .forms import ScheduleModelForm, LicenseModelForm
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib import messages


User = get_user_model()


def monitoring_dashboard(request):
    return render(request, 'monitoring/monitoring_dashboard.html')

class RegistrationListView(View):
    template_name = "monitoring/list-applications.html"
    queryset = Payment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(vet_status=1)
        #return self.queryset

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


def vet_application(request, id):
  payment = get_object_or_404(Payment, pk=id)
  context={'payment': payment,       
           }
  return render(request, 'monitoring/view-applications.html', context)

def approve(request, id):
  if request.method == 'POST':
     payment = get_object_or_404(Payment, pk=id)
     payment.vet_status = 2
     payment.veting_officer = request.user
     payment.save()
     context = {}
     context['object'] = payment
     subject = 'Successful verification of Registration and Payment Details'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [payment.email]
     contact_message = get_template('monitoring/contact_message.txt').render(context)
     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
     messages.success(request, ('Application vetted successfully. Please proceed to Schedule Hospital for Inspection.'))
     return render(request, 'monitoring/verification_successful.html',context)
     
def reject(request, id):
  if request.method == 'POST':
     payment = get_object_or_404(Payment, pk=id)
     payment.vet_status = 3
     payment.save()
     context = {}
     context['object'] = payment
     subject = 'Failed verification of Registration and Payment Details'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [payment.email] 
     contact_message = get_template('monitoring/verification_failed.txt').render(context)
     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
     messages.error(request, ('Verification failed.  Hospital has been sent an email to re-apply with the correct details.'))
     return redirect('/monitoring/'+str(payment.id))


class InspectionScheduleListView(View):
    template_name = "monitoring/inspection_schedule_list.html"
    queryset = Payment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(vet_status=2)
        
    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


class InspectionObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionCreateView(InspectionObjectMixin, View):
    template_name = "monitoring/schedule_inspection.html"
    template_name1 = "monitoring/inspection_scheduled.html"
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = ScheduleModelForm(instance=obj)  
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        form = ScheduleModelForm(request.POST, request.FILES)
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
               'monitoring/inspection_details.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        return render(request, self.template_name1, context)


class InspectionCompletedListView(View):
    template_name = "monitoring/inspections_completed_list.html"
    queryset = Inspection.objects.all()

    def get_queryset(self):
        #return self.queryset.filter(inspection_status=1)
        return self.queryset
        
    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


def verify(request, id):
  inspection = get_object_or_404(Inspection, pk=id)
  
  context={'inspection': inspection,        
           }
  return render(request, 'monitoring/inspections_detail.html', context)

def approve_report(request, id):
  if request.method == 'POST':
     inspection = get_object_or_404(Inspection, pk=id)
     inspection.inspection_status = 2
     inspection.save()

     context = {}
     context['object'] = inspection
     subject = 'Passed Facility Inspection'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [inspection.email]   
     contact_message = get_template('monitoring/inspection_passed.txt').render(context)
     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
     messages.success(request, ('Inspection Report Validation Successful'))    
     return render(request, 'monitoring/inspection_successful.html',context)
    


def reject_report(request, id):
  if request.method == 'POST':
     inspection = get_object_or_404(Inspection, pk=id)
     inspection.inspection_status = 3
     inspection.save()

     context = {}
     context['object'] = inspection
     subject = 'Failed Inpsection Report Validation'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [inspection.email]    
     contact_message = get_template('monitoring/inspection_failed.txt').render(context)
     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
     messages.error(request, ('Inspection failed.  Hospital will be contacted and guided on how to remedy inspection shortfalls.'))
     return render(request, 'monitoring/inspection_failed.html',context)


class LicenseIssueListView(View):
    template_name = "monitoring/license_issue_list.html"
    queryset = Inspection.objects.all()

    def get_queryset(self):
        return self.queryset.filter(inspection_status=4)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class LicenseObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class LicenseDetailView(LicenseObjectMixin, View):
    template_name = "monitoring/licenses_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class IssueLicenseView(LicenseObjectMixin, View):
    template_name = "monitoring/issue_license.html"
    template_name1 = "monitoring/license_issued.html"
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = LicenseModelForm(instance=obj)  
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        form = LicenseModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        context = {}
        obj = self.get_object()
        if obj is not None:        
           context['object'] = obj
           context['form'] = form

           subject = 'Notice of Radiography License Issuance'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [form.cleaned_data.get('email')]

           context['form'] = form
           contact_message = get_template(
               'monitoring/license_issued.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        
        
        return render(request, self.template_name1, context)

class LicensesListView(View):
    template_name = "monitoring/licenses_list.html"
    queryset = License.objects.all()

    def get_queryset(self):
        return self.queryset        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class LicensesDetailView(DetailView):
    model = License
    template_name = 'monitoring/licenses_issued_detail.html'























    


















     




