from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404
from accounts.models import Hospital
from accounts.decorators import monitoring_required
from hospitals.models import Payment, Document, Schedule, Inspection, License, Records, Appraisal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.views import View
from . import views
from .forms import RecordsModelForm
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView
)
from .forms import ScheduleModelForm, LicenseModelForm, AccreditationModelForm
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib import messages
from xhtml2pdf import pisa
import os
from django.contrib.staticfiles import finders
from io import BytesIO
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from itertools import chain
from operator import attrgetter
from django.db.models import Count
from django.db import models
from django.contrib.messages.views import SuccessMessageMixin
import itertools
counter = itertools.count()



User = get_user_model()


class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


def monitoring_dashboard(request):
    return render(request, 'monitoring/monitoring_dashboard.html')

class RegistrationListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/list-applications.html"
    context_object_name = 'object'


    def get_queryset(self):
        return Payment.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(RegistrationListView, self).get_context_data(**kwargs)
        obj['registration_list_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=1)
        #obj['hospital'] = Document.objects.filter(application_no=self.object_list)
        #self.document = Document.objects.get(pk=self.kwargs['pk'])
        return obj

class PaymentObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



#class VetApplication(LoginRequiredMixin, DetailView):
    #template_name = "monitoring/view-applications2.html"
    #model = Payment
    
    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        #context['payment'] = Document.objects.all()
        #context['hospital'] = Hospital.objects.all()
        #context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #return context


#class VetApplication(LoginRequiredMixin, PaymentObjectMixin, View):
    #template_name = "monitoring/view-applications2.html"

    #def get(self, request, id=None, *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #context['object'] = obj
        #context['registration'] = Document.objects.filter (application_no=obj.application_no)
        #return render(request, self.template_name, context) 

class VetApplication(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "monitoring/view-applications2.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)
    

def vet_application(request, id):
  payment = get_object_or_404(Payment, pk=id)
  context={'payment': payment,      
           }
  return render(request, 'monitoring/view-applications.html', context)

def approve(request, id):
  if request.method == 'POST':
     object = get_object_or_404(Payment, pk=id)
     object.vet_status = 2
     object.application_status = 3
     object.vetting_officer = request.user
     object.save()
     context = {}
     context['object'] = object
     context['registration'] = Document.objects.filter (application_no=object.application_no)
     subject = 'Successful verification of Registration and Payment Details'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.hospital_name.hospital_admin]
     contact_message = get_template('monitoring/contact_message.txt').render(context)
     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
     messages.success(request, ('Application vetted successfully. Please proceed to Schedule Hospital for Inspection.'))
     return render(request, 'monitoring/verification_successful.html',context)
 
def reject(request, id):
  if request.method == 'POST':
     object = get_object_or_404(Payment, pk=id)
     object.vet_status = 3
     object.save()
     context = {}
     context['object'] = object
     subject = 'Failed verification of Registration and Payment Details'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.email] 
     contact_message = get_template('monitoring/verification_failed.txt').render(context)
     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
     messages.error(request, ('Verification failed.  Hospital has been sent an email to re-apply with the correct details.'))
     return redirect('/monitoring/'+str(object.id))



class RegistrationObjectMixin(object):
    model = Document
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class InspectionScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspection_schedule_list.html'
    #context_object_name = 'object'

    def get_queryset(self):
        return Payment.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(InspectionScheduleListView, self).get_context_data(**kwargs)
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital__license_type = 'Radiography Practice')
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital__license_type = 'Internship Accreditation')
        return context

#class InspectionCreateView(LoginRequiredMixin, PaymentObjectMixin, View):
    #template_name = 'monitoring/schedule_inspection.html'
    #template_name1 = 'monitoring/inspection_scheduled.html'
    #def get(self, request,  *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
            #form = ScheduleModelForm(instance=obj)
            #context['object'] = obj
            #context['form'] = form

        #return render(request, self.template_name, context)

   
    #def post(self, request,  *args, **kwargs):
        #form = ScheduleModelForm(request.POST)
        #if form.is_valid():
            #form.save()

        #context = {}
        #obj = self.get_object()
        #if obj is not None:
          
           #context['object'] = obj
           #context['form'] = form
           #hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)

           #subject = 'Notice of Facility Inspection'
           #from_email = settings.DEFAULT_FROM_EMAIL
           #to_email = [hospital_admin]

           #context['form'] = form
           #contact_message = get_template(
               #'monitoring/inspection_details.txt').render(context)

           #send_mail(subject, contact_message, from_email,
                     #to_email, fail_silently=False)  
        
        #return render(request, self.template_name1, context)




class InspectionCreateView(LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    template_name = 'monitoring/schedule_inspection.html'
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("monitoring:inspection_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Radiography Practice')
        
        #context = {'object': self.get_object()}
        #context['payment'] = Payment.objects.get(pk=self.object)
        #context['hospital'] = Hospital.objects.get(id=self.kwargs['id'])
        #context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'payment': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.payment = Payment.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.payment.hospital_name
        kwargs['initial']['hospital'] = self.payment.hospital
        kwargs['initial']['application_no'] = self.payment.application_no
        #kwargs['initial']['hospital'] = self.payment.hospital
        
        return kwargs
      

    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)



class AppraisalCreateView(LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    template_name = 'monitoring/schedule_inspection.html'
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("monitoring:inspection_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation')
        
        #context = {'object': self.get_object()}
        #context['payment'] = Payment.objects.get(pk=self.object)
        #context['hospital'] = Hospital.objects.get(id=self.kwargs['id'])
        #context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'payment': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.payment = Payment.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.payment.hospital_name
        kwargs['initial']['hospital'] = self.payment.hospital
        kwargs['initial']['application_no'] = self.payment.application_no
        #kwargs['initial']['hospital'] = self.payment.hospital
        
        return kwargs
      

    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)

class ScheduleObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



class InspectionCreateDetailView(LoginRequiredMixin, ScheduleObjectMixin, View):
    template_name = 'monitoring/inspection_scheduled.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = ScheduleModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)

            subject = 'Notice of Facility Inspection'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]

            context['form'] = form
            contact_message = get_template(
               'monitoring/inspection_details.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)




class InspectionCompletedListView(LoginRequiredMixin, ListView):
    template_name = 'monitoring/inspections_completed_list.html'
    context_object_name = 'object'



    def get_queryset(self):
        return Inspection.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(InspectionCompletedListView, self).get_context_data(**kwargs)

        obj['inspection_qs'] = Inspection.objects.select_related("hospital_name").filter(vet_status=4)
        #obj['inspections_qs'] = Inspection.objects.all()
        obj['appraisal_qs'] = Appraisal.objects.select_related("hospital_name").filter(vet_status=4)
        #obj['appraisals_qs'] = Appraisal.objects.all()
        
        return obj                 



class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionCompletedDetailView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "monitoring/inspections_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)



class AccreditationObjectMixin(object):
    model = Appraisal
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class AccreditationCompletedDetailView(LoginRequiredMixin, AccreditationObjectMixin, View):
    template_name = "monitoring/appraisals_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)


def inspection_report(request, id):
    inspection = get_object_or_404(Inspection, pk=id)
  
    context={'inspection': inspection,        
           }
    return render(request, 'monitoring/inspections_detail.html', context)

def approve_report(request, id):
    if request.method == 'POST':
        object = get_object_or_404(Inspection, pk=id)
        object.inspection_status = 2
        object.application_status = 6
        object.save()

        context = {}
        context['object'] = object
        #context['hospital'] = Hospital.objects.filter(application_no=object.application_no)
        #context['registration'] = Document.objects.filter(application_no=object.application_no)
        subject = 'Passed Facility Inspection'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [object.hospital_name.hospital_admin]   
        contact_message = get_template('monitoring/inspection_passed.txt').render(context)
        send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
        messages.success(request, ('Inspection Report Validation Successful'))    
        return render(request, 'monitoring/inspection_successful.html',context)
    
def approve_appraisal_report(request, id):
    if request.method == 'POST':
      object = get_object_or_404(Appraisal, pk=id)
      object.appraisal_status = 2
      object.application_status = 6
      object.save()

      context = {}
      context['object'] = object
      subject = 'Passed Facility Accreditation'
      from_email = settings.DEFAULT_FROM_EMAIL
      to_email = [object.hospital_name.hospital_admin]   
      contact_message = get_template('monitoring/accreditation_passed.txt').render(context)
      send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
      messages.success(request, ('Internship Accreditation Report Validation Successful'))    
      return render(request, 'monitoring/appraisal_successful.html',context)


def reject_report(request, id):
    if request.method == 'POST':
      object = get_object_or_404(Inspection, pk=id)
      object.inspection_status = 3
      object.save()

      context = {}
      context['object'] = object
      subject = 'Failed Inpsection Report Validation'
      from_email = settings.DEFAULT_FROM_EMAIL
      to_email = [object.hospital_name.hospital_admin]    
      contact_message = get_template('monitoring/inspection_failed.txt').render(context)
      send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
      messages.error(request, ('Inspection failed.  Hospital will be contacted and guided on how to remedy inspection shortfalls.'))
      return render(request, 'monitoring/inspection_failed.html',context)


def reject_appraisal_report(request, id):
    if request.method == 'POST':
      object = get_object_or_404(Appraisal, pk=id)
      object.inspection_status = 3
      object.save()

      context = {}
      context['object'] = object
      subject = 'Failed Accreditation Report Validation'
      from_email = settings.DEFAULT_FROM_EMAIL
      to_email = [object.hospital_name.hospital_admin]    
      contact_message = get_template('monitoring/inspection_failed.txt').render(context)
      send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
      messages.error(request, ('Accreditation failed.  Hospital will be contacted and guided on how to remedy accreditation shortfalls.'))
      return render(request, 'monitoring/inspection_failed.html',context)


def validate(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  
  context={'appraisal': appraisal,        
           }
  return render(request, 'monitoring/appraisals_detail.html', context)


def view_appraisal_report(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  
  context={'appraisal': appraisal,        
           }
  return render(request, 'monitoring/appraisals_report_detail.html', context)

#class LicenseIssueListView(LoginRequiredMixin, ListView):
    #template_name = "monitoring/license_issue_list.html"
    #context_object_name = 'object'
    #queryset = Inspection.objects.all().filter(application_status=7)
    
    #def get_context_data(self, **kwargs):
        #obj = super(LicenseIssueListView, self).get_context_data(**kwargs)
        #obj['inspection'] = self.queryset.filter(application_status=7).count()
        #return obj


class LicenseIssueListView(LoginRequiredMixin, ListView):
    template_name = 'monitoring/license_issue_list.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Inspection.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(LicenseIssueListView, self).get_context_data(**kwargs)

        
        obj['inspection'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice').count()
        obj['inspectionr'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal').count()
        obj['appraisal'] = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation').count()
       
        
        return obj   

class LicenseIssueListTable(LoginRequiredMixin, ListView):
    template_name = "monitoring/license_list_table.html"
    context_object_name = 'object'
    
    def get_queryset(self):
        return Inspection.objects.all()

    
    def get_context_data(self, **kwargs):
        obj = super(LicenseIssueListTable, self).get_context_data(**kwargs)
        obj['issue_license_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')  
        return obj   

class AccreditationIssueListTable(LoginRequiredMixin, ListView):
    template_name = "monitoring/accreditation_list_table.html"
    context_object_name = 'object'
    
    def get_queryset(self):
        return Inspection.objects.all()

    
    def get_context_data(self, **kwargs):
        obj = super(AccreditationIssueListTable, self).get_context_data(**kwargs)
        obj['issue_appraisal_qs'] = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation')
         
        return obj     


class RenewalIssueListTable(LoginRequiredMixin, ListView):
    template_name = "monitoring/renewal_list_table.html"
    context_object_name = 'object'
    
    def get_queryset(self):
        return Inspection.objects.all()

    
    def get_context_data(self, **kwargs):
        obj = super(RenewalIssueListTable, self).get_context_data(**kwargs)
 
        obj['issue_renewal_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')         
        return obj   

class RecordsCreateView(LoginRequiredMixin, CreateView):
    template_name = 'monitoring/create_hospital_records.html'

    form_class = RecordsModelForm

    def get_success_url(self):
        return reverse('monitoring:hospital_record_details', kwargs={'id' : self.object.id})
    

class LicenseDetailView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "monitoring/licenses_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

class AccreditationDetailView(LoginRequiredMixin, AccreditationObjectMixin, View):
    template_name = "monitoring/accreditation_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


#class AccreditationDetailView(LoginRequiredMixin, DetailView):
    #template_name = "monitoring/accreditation_detail.html"
    #model = Appraisal
    
    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        #context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #return context

class RecordsObjectMixin(object):
    model = Records
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class RecordsDetailView(LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "monitoring/hospitals_records_confirmation.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

class HospitalRecordsListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/hospital_records_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Records.objects.all()
        

    def get_context_data(self, **kwargs):
        obj = super(HospitalRecordsListView, self).get_context_data(**kwargs)
        obj['records_qs'] = Records.objects.order_by('-date_visited')
        return obj


class HospitalRecordsDetailView(LoginRequiredMixin, RecordsObjectMixin, View):
    template_name = "monitoring/hospital_records_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class AccreditationObjectMixin(object):
    model = Appraisal
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class IssueLicenseView(LoginRequiredMixin, InspectionObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_license.html'
    form_class = LicenseModelForm

    def get_success_url(self):
        return reverse("monitoring:issued_license_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['license_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.inspection.hospital_name)
        
        
        return context

    def get_initial(self):
       
        return {
            'inspection': self.kwargs["pk"],
           
        }
    
    def get_form_kwargs(self):
        self.inspection = Inspection.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        


        kwargs['initial']['hospital_name'] = self.inspection.hospital_name
        kwargs['initial']['hospital'] = self.inspection.hospital
        kwargs['initial']['payment'] = self.inspection.payment
        kwargs['initial']['application_no'] = self.inspection.application_no
        kwargs['initial']['schedule'] = self.inspection.schedule
        
        return kwargs
    
    
      

    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)


class LicenseObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class LicenseIssuedDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/license_issued.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = LicenseModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           

            subject = 'Notice of Radiography License Issuance'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]

            context['form'] = form
            contact_message = get_template(
               'monitoring/license_issued.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)



class IssueAccreditationView(LoginRequiredMixin, AccreditationObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_accreditation.html'
    form_class = AccreditationModelForm

    def get_success_url(self):
        return reverse("monitoring:issued_accreditation_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accreditation_qs'] = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.appraisal.hospital_name)
        return context

    def get_initial(self):
        
        return {
            'appraisal': self.kwargs["pk"],
            
        }
    
    def get_form_kwargs(self):
        self.appraisal = Appraisal.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        


        kwargs['initial']['hospital_name'] = self.appraisal.hospital_name
        kwargs['initial']['hospital'] = self.appraisal.hospital
        kwargs['initial']['payment'] = self.appraisal.payment
        kwargs['initial']['application_no'] = self.appraisal.application_no
        kwargs['initial']['schedule'] = self.appraisal.schedule
        
        return kwargs
    
       

    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)




class AccreditationIssuedDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/accreditation_issued.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = AccreditationModelForm(instance=obj)
            context['object'] = obj
            hospital_admin = obj.hospital_name.hospital_admin 
           #context['hospital'] = Hospital.objects.filter(hospital_name=self.object)

            subject = 'Notice of Radiography Internship License Issuance'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [hospital_admin]

            context['form'] = form
            contact_message = get_template(
               'monitoring/accreditation_issued.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)






class LicensesListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/licenses_list.html"
    context_object_name = 'object'   

    def get_queryset(self):
        return License.objects.all()  

    def get_context_data(self, **kwargs):
        obj = super(LicensesListView, self).get_context_data(**kwargs)
        obj['license_qs'] = License.objects.order_by('-issue_date')
        return obj    

        
#class LicenseIssuedDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    #template_name = 'monitoring/license_issued.html' 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
            #form = LicenseModelForm(instance=obj)
            #context['object'] = obj
            #context['form'] = form


            #subject = 'Notice of Radiography License Issuance'
            #from_email = settings.DEFAULT_FROM_EMAIL
            #to_email = [request.user.email]

            #context['form'] = form
            #contact_message = get_template(
               #'monitoring/license_issued.txt').render(context)

            #send_mail(subject, contact_message, from_email,
                     #to_email, fail_silently=False)

        #return render(request, self.template_name, context)


class GenerateObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


def link_callback(uri, rel):
    sUrl = settings.STATIC_URL     
    sRoot = settings.STATIC_ROOT    
    mUrl = settings.MEDIA_URL       
    mRoot = settings.MEDIA_ROOT     
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path


class GeneratePdfView(LoginRequiredMixin, GenerateObjectMixin, View):
    
    def get(self, request, *args, **kwargs):
        template = get_template('pdf/license.html')
        context = {
            'object': self.get_object()
        }
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf') 
        return None


class RegisteredHospitalsListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/registered_hospitals_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return License.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(RegisteredHospitalsListView, self).get_context_data(**kwargs)
        obj['hospitals_qs'] = License.objects.order_by('-issue_date')
        return obj
        


class RegisteredObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class RegisterdHospitalsDetailView(LoginRequiredMixin, RegisteredObjectMixin, View):
    template_name = "monitoring/hospital_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)






     




