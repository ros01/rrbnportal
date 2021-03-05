from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.views import View
from .forms import HospitalDetailModelForm, PaymentDetailsModelForm, ReceiptUploadModelForm
from django.urls import reverse, reverse_lazy
from django.template.loader import get_template
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from . import views
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView,
     TemplateView
)
from django.views.generic.edit import ModelFormMixin, FormMixin
from accounts.models import User, Hospital

from django.contrib.auth import get_user_model
from django.conf import settings
from accounts.models import Hospital
from .models import Document, Payment, Inspection, License, Schedule, Appraisal
from django.db.models import Q  
from xhtml2pdf import pisa
import os
from django.contrib.staticfiles import finders
from io import BytesIO
from django.utils.decorators import method_decorator
import uuid

User = get_user_model()


class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


def hospitals_dashboard(request):
     hospitals = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=request.user, application_status=8)
     license = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=request.user, application_status=8).count()
     hospital = Hospital.objects.filter(hospital_admin=request.user)
     context = {
          'hospitals': hospitals,
          'hospital': hospital,
          'license': license
     }
     return render(request, 'hospitals/hospitals_dashboard.html', context)




class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class MyApplicationListView(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_table.html"
    context_object_name = 'object'
    queryset = Document.objects.all()
    def get_queryset(self):
        hospital_admin_id = self.request.user.id
        hospital_instance = Hospital.objects.filter(id=hospital_admin_id)
        return super(MyApplicationListView, self).get_queryset().filter(hospital_name=hospital_instance)
    def get_context_data(self, **kwargs):
        context = super(MyApplicationListView, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Radiography Practice')
        context['hospital_qss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Gov Internship Accreditation')
        context['hospital_qsss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Pri Internship Accreditation')
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, license_type = 'Radiography Practice', application_type = 'New Registration - Radiography Practice')
        context['document_qss'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, license_type = 'Internship Accreditation', application_type = 'New Registration - Government Hospital Internship')
        context['document_qsss'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, license_type = 'Internship Accreditation', application_type = 'New Registration - Private Hospital Internship')
        context['document_qsr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, license_type = 'Radiography Practice', application_type = 'Renewal')
        context['document_qssr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, license_type = 'Internship Accreditation', application_type = 'Renewal')
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['payment_qsss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['payment_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')
        context['payment_qssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal')
        context['payment_verified_qs'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')
        context['payment_verified_qss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['payment_verified_qsss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['payment_verified_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')
        context['payment_verified_qssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal')
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')
        context['schedule_qss'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['schedule_qsss'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['schedule_qsr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')
        context['schedule_qssr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal')
        context['inspection_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')
        context['accreditation_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['accreditation_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['inspection_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')
        context['accreditation_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal')
        context['inspection_approved_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')
        context['accreditation_approved_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['accreditation_approved_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['inspection_approved_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')
        context['accreditation_approved_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal')
        context['registrar_approval_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')
        context['registrar_approval_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['registrar_approval_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['registrar_approval_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')
        context['registrar_approval_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal')
        context['license_issue_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice', hospital__application_type = 'New Registration - Radiography Practice')
        context['license_issue_qss'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['license_issue_qsss'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['license_issue_qsr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal')
        context['license_issue_qssr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal')
        return context 

class HospitalObjectMixin(object):
    model = Hospital
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class StartNewApplication(LoginRequiredMixin, ListView):
    template_name = "hospitals/start_new_application.html"
    context_object_name = 'object'

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Hospital.objects.filter(hospital_admin=self.request.user)

    def get_context_data(self, **kwargs):
        obj = super(StartNewApplication, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        
        return obj  

class StartNewRadApplication(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/register_radiography_practice.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})

    def get_initial(self):
        
        return {
            'hospital_name': self.kwargs["pk"],
            
        }

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
   
     
    def get_context_data(self, **kwargs):
        context = super(StartNewRadApplication, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
       

        return context

    #def get_form_kwargs(self):
        #self.hospital = Hospital.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        ##kwargs['initial']['license_type'] = self.hospital.license_type
        
        #return kwargs


    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)




class StartGovInternshipApplication(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/register_gov_internship_accreditation.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})

    def get_initial(self):
        
        return {
            'hospital_name': self.kwargs["pk"],
            
        }

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
   
     
    def get_context_data(self, **kwargs):
        context = super(StartGovInternshipApplication, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
       

        return context

    #def get_form_kwargs(self):
        #self.hospital = Hospital.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        ##kwargs['initial']['license_type'] = self.hospital.license_type
        
        #return kwargs


    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)


class StartPriInternshipApplication(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/register_pri_internship_accreditation.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:private_hospital_details", kwargs={"id": self.object.id})

    def get_initial(self):
        
        return {
            'hospital_name': self.kwargs["pk"],
            
        }

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
   
     
    def get_context_data(self, **kwargs):
        context = super(StartPriInternshipApplication, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
       
        return context

    #def get_form_kwargs(self):
        #self.hospital = Hospital.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        ##kwargs['initial']['license_type'] = self.hospital.license_type
        
        #return kwargs


    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)

class StartGovInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_gov_internship_accreditation.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})

    #def get_initial(self):
        
        #return {
            #'hospital': self.kwargs["pk"],
            
        #}
     
    def get_form_kwargs(self):
        self.license = License.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        
        return kwargs



    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
   
     
    def get_context_data(self, **kwargs):
        context = super(StartGovInternshipRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
       

        return context

    
    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)



class StartRadiographyLicenseRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_radiography_hospital_license.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:start_radiography_license_renewal_details", kwargs={"id": self.object.id})

    #def get_initial(self):
        #return {
            #'hospital': self.kwargs["pk"],
        #}
    def get_form_kwargs(self):
        self.license = License.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        return kwargs

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        
    def get_context_data(self, **kwargs):
        context = super(StartRadiographyLicenseRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

    def form_invalid(self, form):
        form = self.get_form()
        context = {}
        obj = self.get_object()
        if obj is not None:
           context['object'] = obj
           context['form'] = form 
        return self.render_to_response(context)

class StartApplication(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/hospitals_register.html'
    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})

    def get_initial(self):
        
        return {
            'hospital_name': self.kwargs["pk"],
            
        }

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)
   
     
    def get_context_data(self, **kwargs):
        context = super(StartApplication, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
       

        return context

    def get_form_kwargs(self):
        self.hospital = Hospital.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        #kwargs['initial']['license_type'] = self.hospital.license_type
        
        return kwargs


    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)


class RegistrationObjectMixin(object):
    model = Document
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class HospitalDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/hospitals_reg_confirmation.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)


class PrivateHospitalDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/private_hospital_details.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)




class StartRadiographyLicenseRenewalDetails(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/start_hospital_radiography_license_renewal_details.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)


class FacilityDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    template_name = 'hospitals/hospitals_reg_confirmation.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = HospitalDetailModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital'] = Hospital.objects.filter(hospital_admin=self.request.user)
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Acknowledgment of Interest to Register with RRBN'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/contact_message2.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)



#class FacilityDetailView(LoginRequiredMixin, RegistrationObjectMixin, View):
    #template_name = 'hospitals/facility_reg_confirmation.html' 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {}
        #obj = self.get_object()
        #if obj is not None:
            #form = BasicDetailModelForm(instance=obj)
            #context['object'] = obj
            #context['form'] = form


            #subject = 'Acknowledgment of Interest to Obtain Internship Accreditation'
            #from_email = settings.DEFAULT_FROM_EMAIL
            #to_email = [request.user.email]

            #context['form'] = form
            #contact_message = get_template(
               #'hospitals/contact_message2.txt').render(context)

            #send_mail(subject, contact_message, from_email,
                     #to_email, fail_silently=False)

        #return render(request, self.template_name, context)



class GenerateInvoiceView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_invoice.html"
    model = Document
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class GenerateRenewalInvoice(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_renewal_invoice.html"
    model = Document
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class GenerateAccreditationInvoice(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_accreditation_invoice.html"
    model = Document

    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no
        
        return kwargs
    
    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }

    def get_context_data(self, **kwargs):
        obj = super(GenerateAccreditationInvoice, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #obj['license_history_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user)
        return obj  

class PaymentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/payment_processing.html'
    form_class = PaymentDetailsModelForm

    def get_success_url(self):
        return reverse("hospitals:payment_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name=self.document.hospital_name)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no
        
        return kwargs
         

    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)






class MyLicenseApplicationsHistory(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_license_history.html"
    context_object_name = 'object'


    def get_queryset(self):
        return License.objects.filter(hospital_name__hospital_admin=self.request.user)

    def get_context_data(self, **kwargs):
        obj = super(MyLicenseApplicationsHistory, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        obj['license_history_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user)
        return obj  
        





class RenewalPaymentCreateView(LoginRequiredMixin, RegistrationObjectMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/renewal_payment_processing.html'
    form_class = PaymentDetailsModelForm

    def get_success_url(self):
        return reverse("hospitals:renewal_payment_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user)
        #context['document_qsr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, license_type = 'Radiography Practice', application_type = 'Renewal')
        #context['hospital_qs'] = Hospital.objects.filter(hospital_name=self.object)
        return context

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'hospital': self.kwargs["pk"],
            #'license_type': self.kwargs["pk"]
        }
    
    
    def get_form_kwargs(self):
        self.document = Document.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.document.hospital_name
        kwargs['initial']['application_no'] = self.document.application_no
        
        return kwargs
         

    def form_invalid(self, form):
        form = self.get_form()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form 
          
        return self.render_to_response(context)


class PaymentObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



class PaymentDetailView(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = 'hospitals/payment_details_submission.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = PaymentDetailsModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Receipt of Registration Fee Payment Details'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/payment_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)

class RenewalPaymentDetailView(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = 'hospitals/renewal_payment_details.html' 
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = PaymentDetailsModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
            context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)

            subject = 'Receipt of Registration Fee Payment Details'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [request.user.email]

            context['form'] = form
            contact_message = get_template(
               'hospitals/payment_message.txt').render(context)

            send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name, context)

class PaymentVerificationObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



class PaymentVerificationsView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/payment_verification_details.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class AccreditationPaymentVerifications(LoginRequiredMixin, DetailView):
    template_name = "hospitals/accreditation_payment_verification_details.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class LicenseVerificationsSuccessful(LoginRequiredMixin, DetailView):
    template_name = "hospitals/license_verifications_successful.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class AccreditationVerificationsSuccessful(LoginRequiredMixin, DetailView):
    template_name = "hospitals/accreditation_verifications_successful.html"
    model = Payment
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class ScheduleDetailView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/inspection_schedule_details.html"
    model = Schedule
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class InspectionView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/inspection_report_detail.html"
    model = Inspection
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class AppraisalView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/appraisal_report_detail.html"
    model = Appraisal
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['register'] = Document.objects.filter(hospital_name__hospital_admin=self.request.user)
        #context['payment'] = Payment.objects.filter(hospital_name__hospital_admin=self.request.user)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class AccreditationInspectionApprovedView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/accreditation_report_approved.html"
    model = Appraisal
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context



class InspectionApprovedView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/inspection_report_approved.html"
    model = Inspection
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class AppraisalObjectMixin(object):
    model = Appraisal
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionListView(View):
    template_name = "hospitals/inspection_report_table.html"
    queryset = Inspection.objects.all()

    def get_queryset(self):
        #return self.queryset.filter(inspection_status=2)
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)




class LicenseIssuanceView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/license_issuance.html"
    model = Inspection
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


class InternshipLicenseIssuanceView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/internship_license_issuance.html" 
    model = Appraisal
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital'] = Hospital.objects.filter(hospital_name=self.object)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context 



#class InternshipLicenseIssuanceView(LoginRequiredMixin, AppraisalObjectMixin, View):
    #template_name = "hospitals/internship_license_issuance.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)            

#class InspectionView(LoginRequiredMixin, InspectionObjectMixin, View):
    #template_name = "hospitals/inspection_report_detail.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)

#class VerificationsSuccessfulView(LoginRequiredMixin, PaymentVerificationObjectMixin, View):
    #template_name = "hospitals/verifications_successful.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #context = {'hospital_qs': Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)}
        #return render(request, self.template_name, context)

#class ScheduleDetailView(LoginRequiredMixin, ScheduleObjectMixin, View):
    #template_name = "hospitals/inspection_schedule_details.html" 
    #def get(self, request, id=None, *args, **kwargs):
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context)


class LicenseObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj   


class MyLicensesDetailView(LoginRequiredMixin, DetailView):
    template_name = "hospitals/license_application_summary.html"
    model = License
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

class StartLicenseRenewal(LoginRequiredMixin, DetailView):
    template_name = "hospitals/start_renewal.html"
    model = License
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context

#class StartLicenseRenewal(LoginRequiredMixin, LicenseObjectMixin, View):
    #template_name = "hospitals/start_renewal.html" # DetailView
    #def get(self, request, id=None, *args, **kwargs):
        # GET method
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context) 




#class StartApplication(LoginRequiredMixin, CreateView):
    #template_name = 'hospitals/hospitals_register.html'

    #form_class = HospitalDetailModelForm

    #def get_success_url(self):
        #return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})



class HospitalRenewView(CreateView):
    template_name = 'hospitals/hospitals_register.html'

    form_class = HospitalDetailModelForm
  


def reg_table(request):
     return render(request, 'hospitals/reg_table.html')


class RegisterFacility(LoginRequiredMixin, CreateView):
    template_name = 'hospitals/hospitals_register.html'

    form_class = HospitalDetailModelForm

    def get_success_url(self):
        return reverse("hospitals:facility_details", kwargs={"id": self.object.id})


class PaymentProcessing(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "hospitals/payment_processing.html"
    template_name1 = 'hospitals/payment_details_submitted.html'
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = PaymentDetailsModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request,  *args, **kwargs):
        form = PaymentDetailsModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form

           subject = 'Receipt of Accreditation Fee Payment Details'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [request.user.email]

           context['form'] = form
           contact_message = get_template(
               'hospitals/payment_message2.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)  
        
        return render(request, self.template_name1, context)




class PaymentConfirmation(LoginRequiredMixin, PaymentVerificationObjectMixin, View):
    template_name = "hospitals/payment_verification_detail.html" 
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)



class PaymentVerificationListView(LoginRequiredMixin, View):
    template_name = "hospitals/payment_verification_table.html"
    queryset = Payment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


class ScheduleListView(LoginRequiredMixin, View):
    template_name = "hospitals/inspection_schedule_table.html"
    queryset = Schedule.objects.all()

    def get_queryset(self):
        #return self.queryset.filter(inspection_zone="Enugu")
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class ScheduleObjectMixin(object):
    model = Schedule
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 



class MyLicensesListView(LoginRequiredMixin, View):
    template_name = "hospitals/my_license_table.html"
    queryset = License.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)



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





class DownloadLicense(LoginRequiredMixin, LicenseObjectMixin, View):
    
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


#class StartLicenseRenewal(LoginRequiredMixin, LicenseObjectMixin, View):
    #template_name = "hospitals/start_renewal.html" # DetailView
    #def get(self, request, id=None, *args, **kwargs):
        # GET method
        #context = {'object': self.get_object()}
        #return render(request, self.template_name, context) 






@login_required
def lookup(request):
   registration = Registration.objects.all()

   context = {
     'registration': registration
   }
   return render(request, 'hospitals/hospitals_lookup.html', context)


