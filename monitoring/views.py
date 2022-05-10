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
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView
)
from .forms import *
from .models import *
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib import messages
from xhtml2pdf import pisa
import os
from django.contrib.staticfiles import finders
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from itertools import chain
from operator import attrgetter
from django.db.models import Count
from django.db import models
from django.contrib.messages.views import SuccessMessageMixin
import itertools
counter = itertools.count()
import time
from django.http import JsonResponse
from itertools import chain
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.pagesizes import landscape, portrait
from django.contrib import admin
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

User = get_user_model()


class LoginRequiredMixin(object):
    #@classmethod
    #def as_view(cls, **kwargs):
        #view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        #return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

@login_required
def monitoring_dashboard(request):
    return render(request, 'monitoring/monitoring_dashboard.html')

@login_required
def upload_internship_centers(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('monitoring:monitoring_dashboard')
    else:
        form = DocumentForm()
    return render(request, 'monitoring/internship_centers.html', {
        'form': form
    })

class UploadInternshipList1(View):
    def get(self, request):
        internship_list = InternshipList.objects.all()
        return render(self.request, 'monitoring/file_upload.html', {'list': internship_list})

    def post(self, request):
        form = InternshipListForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            document = form.save()
            data = {'is_valid': True, 'name': document.file.name, 'url': document.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)

class UploadInternshipList(View):
    def get(self, request):
        internship_list = InternshipList.objects.all()
        return render(self.request, 'monitoring/file_upload.html', {'list': internship_list})

    def post(self, request):
        time.sleep(1)
        form = InternshipListForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            document = form.save()
            data = {'is_valid': True, 'name': document.file.name, 'url': document.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


@login_required
def clear_database(request):
    for document in InternshipList.objects.all():
        document.file.delete()
        document.delete()
    return redirect(request.POST.get('next'))

class MyUserAccount(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'monitoring/my_profile.html')



class AllHospitalsView(LoginRequiredMixin, ListView):
    template_name = "monitoring/hospitals_application_table2.html"
    context_object_name = 'object'
    # model = Document 

    def get_queryset(self):
         queryset = Document.objects.order_by('submission_date')
         return queryset
    
    
    def get_context_data(self, **kwargs):
        context = super(AllHospitalsView, self).get_context_data(**kwargs)
        hospital_rpp = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Radiography Practice Permit')
        context['hospital_rpp'] = hospital_rpp
        hospital_gia = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Gov Internship Accreditation')
        hospital_pia = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Pri Internship Accreditation')
        hospital_rppr = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Radiography Practice Permit Renewal')
        hospital_piar = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Pri Internship Accreditation Renewal')
        hospital_giar = Hospital.objects.select_related("hospital_admin").filter(application_status=1, type = 'Gov Internship Accreditation Renewal')
        
        stage_one = Hospital.objects.select_related("hospital_admin").filter(application_status=1)
        context['stage_one'] = stage_one


        document_rpp = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Radiography Practice Permit', application_type = 'New Registration - Radiography Practice Permit')
        context['document_rpp'] = document_rpp
        document_gia = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Government Hospital Internship')
        document_pia = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Private Hospital Internship')
        document_rppr = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Radiography Practice Permit', application_type = 'Renewal - Radiography Practice Permit')
        document_piar = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Private Hospital Internship')
        document_giar = Document.objects.select_related("hospital_name").filter(application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Government Hospital Internship')
       
        stage_two = Document.objects.select_related("hospital_name").filter(application_status=1)
        context['stage_two'] = stage_two


        payment_rpp = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        payment_gia = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        payment_pia = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        payment_rppr = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        payment_piar = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        payment_giar = Payment.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_three = Payment.objects.select_related("hospital_name").filter(application_status=2)
        context['stage_three'] = stage_three

        payment_vrpp = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        payment_vgia = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        payment_vpia = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        payment_vrppr = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        payment_vpiar = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        payment_vgiar = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_four = Payment.objects.select_related("hospital_name").filter(application_status=3)
        context['stage_four'] = stage_four

        schedule_rpp = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        schedule_gia = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        schedule_pia = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['schedule_qsr'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        schedule_piar = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        schedule_giar = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_five = Schedule.objects.select_related("hospital_name").filter(application_status=4)
        context['stage_five'] = stage_five

        inspection_rpp = Inspection.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        accreditation_gia = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        accreditation_pia = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #inspection_qsr = Inspection.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        accreditation_piar = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        accreditation_giar = Appraisal.objects.select_related("hospital_name").filter(application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        
        stage_six = Inspection.objects.select_related("hospital_name").filter(application_status=5)
        context['stage_six'] = stage_six

        stage_seven = Appraisal.objects.select_related("hospital_name").filter(application_status=5)
        context['stage_seven'] = stage_seven


        inspection_arpp = Inspection.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        accreditation_agia = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        accreditation_apia = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['inspection_approved_qsr'] = Inspection.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        accreditation_apiar = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        accreditation_agiar = Appraisal.objects.select_related("hospital_name").filter(application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_eight = Inspection.objects.select_related("hospital_name").filter(application_status=6)
        context['stage_eight'] = stage_eight

        stage_nine = Appraisal.objects.select_related("hospital_name").filter(application_status=6)
        context['stage_nine'] = stage_nine


        registrar_arpp = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        registrar_agia = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        registrar_apia = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['registrar_approval_qsr'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        registrar_arppr = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        registrar_apiar = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        registrar_agiar = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_ten = Inspection.objects.select_related("hospital_name").filter(application_status=7)
        context['stage_ten'] = stage_ten

        stage_eleven = Appraisal.objects.select_related("hospital_name").filter(application_status=7)
        context['stage_eleven'] = stage_eleven


        license_irpp = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        license_igia = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        license_ipia = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        license_irppr = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        license_ipiar = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        license_igiar = License.objects.select_related("hospital_name").filter(application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')

        stage_twelve = License.objects.select_related("hospital_name").filter(application_status=8)
        context['stage_twelve'] = stage_twelve
        
        all_hospitals_list = sorted(chain(stage_one, stage_two, stage_three, stage_four, stage_five, stage_six, stage_seven, stage_eight, stage_nine, stage_ten, stage_eleven, stage_twelve), key=lambda instance: instance.pk,reverse=True)

        # all_hospitals_list = sorted(chain(hospital_rpp, hospital_gia, hospital_pia, hospital_rppr, hospital_piar, hospital_giar, document_rpp, document_gia, document_pia, document_rppr, document_piar, document_giar, payment_rpp, payment_gia, payment_pia, payment_rppr, payment_piar, payment_giar, payment_vrpp, payment_vgia, payment_vpia, payment_vrppr, payment_vpiar, payment_vgiar, schedule_rpp, schedule_gia, schedule_pia, schedule_piar, schedule_pia, schedule_piar, schedule_giar, inspection_rpp, accreditation_gia, accreditation_pia, accreditation_piar, accreditation_giar, inspection_arpp, accreditation_agia, accreditation_apia, accreditation_apiar, accreditation_agiar, registrar_arpp, registrar_agia, registrar_apia, registrar_arppr, registrar_apiar, registrar_agiar, license_irpp, license_igia, license_ipia, license_irppr, license_ipiar, license_igiar), key=lambda instance: instance.date,reverse=True)
        context['all_hospitals_list'] = all_hospitals_list
        return context 



class HospitalProfileDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_profile_details.html"
    model = Hospital

class HospitalRegistrationDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_registration_details.html"
    model = Document

class HospitalPaymentDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_payment_details.html"
    model = Payment


class HospitalVerificationDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_verification_details.html"
    model = Payment

class HospitalScheduleDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_schedule_details.html"
    model = Schedule

class HospitalInspectionDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_inspection_details.html"
    model = Inspection

class HospitalAccreditationDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_accreditation_details.html"
    model = Appraisal


class HospitalInspectionApprovalDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_inspection_approval_details.html"
    model = Inspection


class HospitalAccreditationApprovalDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_accreditation_approval_details.html"
    model = Appraisal

class HospitalInspectionRegistrarApprovalDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_inspection_registrar_approval_details.html"
    model = Inspection

class HospitalAccreditationRegistrarApprovalDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_accreditation_registrar_approval_details.html"
    model = Appraisal
    

class HospitalLicenseDetails(LoginRequiredMixin, DetailView):
    template_name = "monitoring/hospital_license_details.html"
    model = License


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

@login_required
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
     send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
     messages.success(request, ('Application vetted successfully. Please proceed to Schedule Hospital for Inspection in case of New Practice Permit Application or Internship Accreditation Application.'))
     return render(request, 'monitoring/verification_successful.html',context)

@login_required 
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
     send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
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
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
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
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit', application_no=self.payment.application_no)
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', application_no=self.payment.application_no)
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
        return self.render_to_response(self.get_context_data())



class AppraisalCreateView(LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = Schedule
    template_name = 'monitoring/schedule_inspection.html'
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("monitoring:inspection_details", kwargs={"id": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship', application_no=self.payment.application_no)
        context['payment_qsss'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship', application_no=self.payment.application_no)
        #context['payment_qsr'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit', application_no=self.payment.application_no)
        context['payment_qssr'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship', application_no=self.payment.application_no)
        context['payment_qgssr'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital_name=self.payment.hospital_name, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship', application_no=self.payment.application_no)
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
        return self.render_to_response(self.get_context_data())

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
                     to_email, fail_silently=True)
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

@login_required
def inspection_report(request, id):
    inspection = get_object_or_404(Inspection, pk=id)
  
    context={'inspection': inspection,        
           }
    return render(request, 'monitoring/inspections_detail.html', context)

@login_required
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
        send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
        messages.success(request, ('Inspection Report Validation Successful'))    
        return render(request, 'monitoring/inspection_successful.html',context)


@login_required   
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
      send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
      messages.success(request, ('Internship Accreditation Report Validation Successful'))    
      return render(request, 'monitoring/appraisal_successful.html',context)

@login_required
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
      send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
      messages.error(request, ('Inspection failed.  Hospital will be contacted and guided on how to remedy inspection shortfalls.'))
      return render(request, 'monitoring/inspection_failed.html',context)

@login_required
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
      send_mail(subject, contact_message, from_email, to_email, fail_silently=True)
      messages.error(request, ('Accreditation failed.  Hospital will be contacted and guided on how to remedy accreditation shortfalls.'))
      return render(request, 'monitoring/inspection_failed.html',context)

@login_required
def validate(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  context={'appraisal': appraisal,        
           }
  return render(request, 'monitoring/appraisals_detail.html', context)

@login_required
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
        obj['inspection'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit').count()
        obj['permitr'] = Payment.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit').count()
        obj['appraisal'] = Appraisal.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Internship Accreditation').count()   
        return obj   

class LicenseIssueListTable(LoginRequiredMixin, ListView):
    template_name = "monitoring/license_list_table.html"
    context_object_name = 'object'  
    def get_queryset(self):
        return Inspection.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(LicenseIssueListTable, self).get_context_data(**kwargs)
        obj['issue_license_qs'] = Inspection.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')  
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
    template_name = "monitoring/renewal_list_table2.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return Payment.objects.all() 
    def get_context_data(self, **kwargs):
        obj = super(RenewalIssueListTable, self).get_context_data(**kwargs)
        obj['issue_renewal_qs'] = Payment.objects.select_related("hospital_name").filter(application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')         
        return obj   

class RecordsCreateView(LoginRequiredMixin, CreateView):
    template_name = 'monitoring/create_hospital_records.html'
    form_class = RecordsModelForm
    def get_success_url(self):
        return reverse('monitoring:hospital_record_details', kwargs={'id' : self.object.id})

class PermitRenewalDetails(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "monitoring/practice_permit_renewal_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)   

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
        return self.render_to_response(self.get_context_data())

  

class IssueRadCertPermitView(LoginRequiredMixin, InspectionObjectMixin, SuccessMessageMixin, CreateView):
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
        return self.render_to_response(self.get_context_data())

class IssueRadPracticePermitView(LoginRequiredMixin, InspectionObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_license.html'
    form_class = LicenseModelForm
    def get_success_url(self):
        return reverse("monitoring:rad_practice_permit_details", kwargs={"id": self.object.id})
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
        return self.render_to_response(self.get_context_data())



class IssueRadPracticePermitRenewal(LoginRequiredMixin, PaymentObjectMixin, SuccessMessageMixin, CreateView):
    model = License
    template_name = 'monitoring/issue_practice_permit_renewal.html'
    form_class = PermitRenewalModelForm
    def get_success_url(self):
        return reverse("monitoring:rad_practice_permit_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['license_qs'] = Payment.objects.select_related("hospital_name").filter(application_status=7, hospital_name=self.payment.hospital_name)     
        return context
    def get_initial(self):    
        return {
            'payment': self.kwargs["pk"],      
        }
    def get_form_kwargs(self):
        self.payment = Payment.objects.get(pk=self.kwargs['pk'])
        kwargs = super().get_form_kwargs()
        kwargs['initial']['hospital_name'] = self.payment.hospital_name
        kwargs['initial']['hospital'] = self.payment.hospital
        #kwargs['initial']['payment'] = self.inspection.payment
        kwargs['initial']['application_no'] = self.payment.application_no
        #kwargs['initial']['schedule'] = self.inspection.schedule 
        return kwargs  
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())




class LicenseObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class LicenseIssuedDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/license_issued2.html' 
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
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)


class RegPermitCertDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/license_issued2.html' 
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
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)


class RadPracticePermitDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/practice_permit_issued.html' 
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
                     to_email, fail_silently=True)

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
        return self.render_to_response(self.get_context_data())

    #def form_invalid(self, form):
        #form = self.get_form()

        #context = {}
        #obj = self.get_object()
        #if obj is not None:
          
           #context['object'] = obj
           #context['form'] = form 
          
        #return self.render_to_response(context)




class AccreditationIssuedDetailView(LoginRequiredMixin, LicenseObjectMixin, View):
    template_name = 'monitoring/accreditation_issued2.html' 
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
                     to_email, fail_silently=True)
        return render(request, self.template_name, context)



class RadRegCerttificateListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/radiography_reg_cert_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(RadRegCerttificateListView, self).get_context_data(**kwargs)
        obj['rad_cert_reg'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit').order_by('-issue_date')
        return obj    


class RadPracticePermitListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/rad_practice_permit_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(RadPracticePermitListView, self).get_context_data(**kwargs)
        obj['rad_practice_permit'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit').order_by('-issue_date')
        return obj  


class AccreditationCertificateListView(LoginRequiredMixin, ListView):
    template_name = "monitoring/accreditation_cert_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(AccreditationCertificateListView, self).get_context_data(**kwargs)
        obj['accreditation_cert'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation').order_by('-issue_date')   
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
                     #to_email, fail_silently=True)

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



class GenerateLicense(LoginRequiredMixin, GenerateObjectMixin, View):   
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



def getPDF(request, id):
    """Returns PDF as a binary stream."""

    # Use your favourite templating language here to create the RML string.
    # The generated document might depend on the web request parameters,
    # database lookups and so on - we'll leave that up to you.
    license = get_object_or_404(License, pk=id)
    context={'license': license,      
           }
    #return render(request, 'pdf/elicense.rml', context)
    t = Template(open('pdf/elicense.rml', context).read())
    c = Context({"name": name})
    rml = t.render(c)

    buf = cStringIO.StringIO()
    rml2pdf.go(rml, outputFileName=buf)
    pdfData = buf.read()

    response = HttpResponse(mimetype='application/pdf')
    response.write(pdfData)
    response['Content-Disposition'] = 'attachment; filename=output.pdf'
    return response


    #rml = getRML(request)  

    #buf = StringIO()

    #rml2pdf.go(rml, outputFileName=buf)
    #buf.reset()
    #pdfData = buf.read()

    #response = HttpResponse(mimetype='application/pdf')
    #response.write(pdfData)
    #response['Content-Disposition'] = 'attachment; filename=output.pdf'
    #return response


@login_required
def download_rad_cert_reg(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=portrait(A4))
    
    object = get_object_or_404(License, pk=id)

    image_path1 = '%s/img/cert_border1.jpeg' % settings.STATIC_ROOT
    image_path2 = '%s/img/logo_small.png' % settings.STATIC_ROOT
    image_path3 = '%s/img/cert_seal4.jpeg' % settings.STATIC_ROOT
    image_path4 = '%s/img/ceo_sign.jpg' % settings.STATIC_ROOT
    p.drawImage(image_path1, 0, 0, width=595, height=840)

    p.drawImage(image_path2, 250, 690, width=90, height=90)

  # Header Text
    p.setFont("Helvetica-Bold", 16, leading=None)
    p.drawCentredString(300, 660, 'THE RADIOGRAPHERS REGISTRATION BOARD OF NIGERIA')

  # Body Text
    p.setFont("Helvetica", 12, leading=None)
    p.drawCentredString(300, 645, 'Established by Decree 42, 1987 (now Cap R1 LFN 2004)')

    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(300, 580, 'Certificate of Registration of Practice')

    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(300, 560, 'This is to certify that')

    p.setFont("Helvetica", 22, leading=None)
    p.drawCentredString(300, 500, str(object.hospital_name))

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 480, str(object.hospital.facility_address))

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 420, 'having satisfied all laid down conditions of the')

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 400, 'Radiographers Registration Board of Nigeria')

    p.setFont("Helvetica", 16, leading=None)
    p.drawString(200, 330, 'have today')

    p.setFont("Helvetica", 16, leading=None)
    p.drawString(290, 330, str(object.issue_date))

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 250, 'been registered as a practicing centre for')

    LINE_1 = 508

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 230, str(object.hospital.equipment))



    p.setFont("Helvetica", 14, leading=None)
    p.drawString(330, 130, 'Registrar/Secretary')

    p.drawImage(image_path3, 55, 90, width=120, height=120)
    p.drawImage(image_path4, 340, 145, width=110, height=60)

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 70, 'This Certificate shall remain the propery of Radiographers Registration Board of Nigeria (RRBN)')

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 60, 'and shall, on demand, be surrendered to the Board')

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 40, 'E-mail: info@rrbn.gov.ng')
    

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='certificate_of_registration_of_practice.pdf')


 

@login_required
def download_rad_practice_permit(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=(A4))
    object = get_object_or_404(License, pk=id)
    image_path1 = '%s/img/cert_border6.jpeg' % settings.STATIC_ROOT
    image_path2 = '%s/img/logo_small.png' % settings.STATIC_ROOT
    image_path3 = '%s/img/cert_seal4.jpeg' % settings.STATIC_ROOT
    image_path4 = '%s/img/ceo_sign.jpg' % settings.STATIC_ROOT
    #image_path5 = '%s/img/passport.jpg' % settings.STATIC_ROOT
    p.drawImage(image_path1, 0, 0, width=595, height=840)
    p.drawImage(image_path2, 150, 550, width=115, height=115)

  # Header Text
    p.setFont("Helvetica-Bold", 16, leading=None)
    p.drawCentredString(300, 780, 'THE RADIOGRAPHERS REGISTRATION BOARD OF NIGERIA')

  # Body Text
    p.setFont("Helvetica", 12, leading=None)
    p.drawCentredString(300, 765, 'Established by Decree 42, 1987 (now Cap R1 LFN 2004)')
    
    p.setFont("Helvetica", 10, leading=None)
    p.drawCentredString(455, 735, 'PERMIT NO: '+ str(object.license_no))

    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(150, 700, 'Year')

    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(200, 700, str(object.issue_date.strftime("%Y")))


    p.setFont("Helvetica-Bold", 18, leading=None)
    p.drawCentredString(360, 700, 'Registration of Practice Permit')

    p.roundRect(355, 555, 110, 115, 4, stroke=1, fill=0)


    p.drawImage((object.hospital.radiographer_in_charge_passport.path), 356, 556, width=108, height=114)


    p.setFont("Helvetica", 7, leading=None)
    p.drawCentredString(410, 545, 'R.I.C RRBN LICENSE NO: '+ str(object.hospital.radiographer_in_charge_license_no))

    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(300, 485, 'This Permit is Issued to')

    p.setFont("Helvetica", 22, leading=None)
    p.drawCentredString(300, 425, str(object.hospital_name))


    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 370, 'Located at ' + str(object.hospital.facility_address))

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 305, 'In partial fullfillment of the conditions as a')

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 280, 'Radiography Practicing Hospital/Centre')

    p.setFont("Helvetica", 14, leading=None)
    p.drawString(250, 130, 'Registrar/Secretary')

    p.setFont("Helvetica", 16, leading=None)
    p.drawString(390, 170, str(object.issue_date))

    p.setFont("Helvetica", 14, leading=None)
    p.drawString(410, 130, 'Date')

    p.drawImage(image_path3, 95, 110, width=120, height=120)
    p.drawImage(image_path4, 260, 145, width=110, height=60)

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 70, 'This permit shall remain the propery of Radiographers Registration Board of Nigeria (RRBN)')

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 60, 'and shall, on demand, be surrendered to the Board')

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(300, 40, 'E-mail: info@rrbn.gov.ng')
    

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='registration_of_practice_permit.pdf')   


@login_required
def download_accreditation_cert(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    object = get_object_or_404(License, pk=id)

    image_path1 = '%s/img/cert_border5.jpeg' % settings.STATIC_ROOT
    image_path2 = '%s/img/logo_small.png' % settings.STATIC_ROOT
    image_path3 = '%s/img/cert_seal4.jpeg' % settings.STATIC_ROOT
    image_path4 = '%s/img/ceo_sign.jpg' % settings.STATIC_ROOT
    p.drawImage(image_path1, 0, 0, width=842, height=595)

    p.drawImage(image_path2, 380, 478, width=90, height=90)

  # Header Text
    p.setFont("Helvetica-Bold", 22, leading=None)
    p.drawCentredString(421, 450, 'THE RADIOGRAPHERS REGISTRATION BOARD OF NIGERIA')

  # Body Text
    p.setFont("Helvetica", 12, leading=None)
    p.drawCentredString(421, 435, 'Established by Decree 42, 1987 (now Cap R1 LFN 2004)')

    p.setFont("Helvetica", 9, leading=None)
    p.drawCentredString(670, 415, 'Certificate No: '+ str(object.license_no))

    p.setFont("Helvetica-Bold", 22, leading=None)
    p.drawCentredString(421, 390, 'Accreditation Certificate')

    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(421, 360, 'This is to certify that')

    p.setFont("Helvetica", 22, leading=None)
    p.drawCentredString(421, 320, str(object.hospital_name))

    p.setFont("Helvetica", 14, leading=None)
    p.drawCentredString(421, 300, str(object.hospital.facility_address))

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 263, 'having satisfied all laid down conditions by Radiographers Registration Board of Nigeria')

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 245, 'for accreditation of hospital/centre for training of Intern Radiographers')

    p.setFont("Helvetica", 16, leading=None)
    p.drawString(330, 200, 'have this day')

    p.setFont("Helvetica", 16, leading=None)
    p.drawString(435, 200, str(object.issue_date))

    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 160, 'been granted')


    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(455, 160, str(object.license_class))


    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(300, 140, 'for the period')


    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(400, 140, str(object.issue_date))


    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(455, 140, 'to')


    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(511, 140, str(object.expiry_date))




    p.setFont("Helvetica", 14, leading=None)
    p.drawString(130, 100, 'Registrar/Secretary')

    p.drawImage(image_path3, 605, 65, width=120, height=120)
    p.drawImage(image_path4, 130, 110, width=110, height=60)

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(425, 45, 'This Certificate shall remain the propery of Radiographers Registration Board of Nigeria (RRBN) and shall, on demand, be surrendered to the Board')

    p.setFont("Helvetica", 11, leading=None)
    p.drawCentredString(425, 30, 'E-mail: info@rrbn.gov.ng')
    

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='accreditation_certificate.pdf')   


PAGESIZE = (140 * mm, 216 * mm)
BASE_MARGIN = 5 * mm

class PdfCreator:
    def add_page_number(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        page_number_text = "%d" % (doc.page)
        canvas.drawCentredString(
            0.75 * inch,
            0.75 * inch,
            page_number_text
        )
        canvas.restoreState()
    def get_body_style(self):
        sample_style_sheet = getSampleStyleSheet()
        body_style = sample_style_sheet['BodyText']
        body_style.fontSize = 18
        return body_style
    
    def build_pdf(self):
        pdf_buffer = BytesIO()
        my_doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=PAGESIZE,
            topMargin=BASE_MARGIN,
            leftMargin=BASE_MARGIN,
            rightMargin=BASE_MARGIN,
            bottomMargin=BASE_MARGIN
        )
        body_style = self.get_body_style()
        flowables = [
            Paragraph("First paragraph", body_style),
            Paragraph("Second paragraph", body_style)
        ]
        my_doc.build(
            flowables,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )
        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()
        return pdf_value


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






     




