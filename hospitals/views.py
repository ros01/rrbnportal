from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.list import MultipleObjectMixin
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
from django.shortcuts import get_list_or_404

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
from itertools import chain



from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.pagesizes import landscape, portrait
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.views.generic.detail import SingleObjectMixin




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


class MyApplicationListView2(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_table3.html"
    context_object_name = 'object'
    model = Document
         
    def get_context_data(self, **kwargs):
        context = super(MyApplicationListView, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Radiography Practice')
        context['hospital_qss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Gov Internship Accreditation')
        context['hospital_qsss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, hospital_admin__type = 'Pri Internship Accreditation')
        q1 = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Radiography Practice', application_type = 'Renewal - Radiography Practice')
        q2 = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        q3 = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        q4 = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        q5 = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice', hospital__application_type = 'Renewal - Radiography Practice')
        context['li_stage'] =  chain(q5, q4, q3, q2, q1)
        context['reg_stage'] = chain(q4, q3)
        context['pvs_stage'] = chain(q3, q2)
        context['pym_stage'] = q2
        context['doc_stage'] = q1        
        return context

class MyApplicationListView(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_table.html"
    context_object_name = 'object'
    model = Document


    # def get_queryset(self, **kwargs):
    #    qs = super().get_queryset(**kwargs)
    #    return qs.filter(application_no=self.kwargs['application_no'])
   
    
    def get_context_data(self, **kwargs):
        context = super(MyApplicationListView, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Radiography Practice Permit')
        context['hospital_qss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Gov Internship Accreditation')
        context['hospital_qsss'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Pri Internship Accreditation')
        context['hospital_qsr'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Radiography Practice Permit Renewal')
        context['hospital_qssr'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Pri Internship Accreditation Renewal')
        context['hospital_qgssr'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user, type = 'Gov Internship Accreditation Renewal')
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Radiography Practice Permit', application_type = 'New Registration - Radiography Practice Permit')
        context['document_qss'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Government Hospital Internship')
        context['document_qsss'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'New Registration - Private Hospital Internship')
        context['document_qsr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Radiography Practice Permit', application_type = 'Renewal - Radiography Practice Permit')
        context['document_qssr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Private Hospital Internship')
        context['document_qgssr'] = Document.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=1, license_type = 'Internship Accreditation', application_type = 'Renewal - Government Hospital Internship')
        context['payment_qs'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['payment_qss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['payment_qsss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['payment_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['payment_qssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['payment_qgssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['payment_verified_qs'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['payment_verified_qss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['payment_verified_qsss'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['payment_verified_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['payment_verified_qssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['payment_verified_qgssr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=3, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['schedule_qss'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['schedule_qsss'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['schedule_qsr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['schedule_qssr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['schedule_qgssr'] = Schedule.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=4, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['inspection_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['accreditation_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['accreditation_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['inspection_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['accreditation_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['accreditation_qgssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=5, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['inspection_approved_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['accreditation_approved_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['accreditation_approved_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['inspection_approved_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['accreditation_approved_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['accreditation_approved_qgssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=6, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['registrar_approval_qs'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['registrar_approval_qss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['registrar_approval_qsss'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        #context['registrar_approval_qsr'] = Inspection.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['registrar_approval_qsr'] = Payment.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['registrar_approval_qssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['registrar_approval_qgssr'] = Appraisal.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=7, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        context['license_issue_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit')
        context['license_issue_qss'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Government Hospital Internship')
        context['license_issue_qsss'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'New Registration - Private Hospital Internship')
        context['license_issue_qsr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        context['license_issue_qssr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Private Hospital Internship')
        context['license_issue_qgssr'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, application_status=8, hospital__license_type = 'Internship Accreditation', hospital__application_type = 'Renewal - Government Hospital Internship')
        # print (context)
        return context 

class MyApplicationListView3(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_applications_table.html"
    context_object_name = 'object'
    model = Document
   
    def get_context_data(self, *args, **kwargs):
        context = super(MyApplicationListView, self).get_context_data(*args, **kwargs)
        print(dir(context.get('page_obj')))
        return context

    def get_queryset(self):
        request = self.request
        qs = Document.objects.all()
        query = request.GET.get('q')
        user = self.request.user
        if query:
            qs = qs.filter(title__icontains=query)
        # if user.is_authenticated():
        #     qs = qs.owned(user)
        return qs 




class HospitalObjectMixin(object):
    model = Hospital
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class StartNewApplication(LoginRequiredMixin, HospitalObjectMixin, ListView):
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
    
    #def form_invalid(self, form):
        #form = self.get_form()
        #context = {}
        #obj = self.get_object()
        #if obj is not None: 
           #context['object'] = obj
           #context['form'] = form  
        #return self.render_to_response(context)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

class StartNewPracticePermitRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_radiography_hospital_license.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:start_radiography_license_renewal_details", kwargs={"id": self.object.id})
    def get_initial(self):
        return {
            'hospital_name': self.kwargs["pk"],
        }
    
    #def get_form_kwargs(self):
        #self.license = License.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        #kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        #return kwargs

    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user)    
    def get_context_data(self, **kwargs):
        context = super(StartNewPracticePermitRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class StartNewPriInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_pri_internship_accreditation.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:private_hospital_details", kwargs={"id": self.object.id})
    def get_initial(self):   
        return {
            'hospital_name': self.kwargs["pk"],        
        }
    #def get_form_kwargs(self):
        #self.license = License.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        #kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        #return kwargs
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user) 
    def get_context_data(self, **kwargs):
        context = super(StartNewPriInternshipRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())


class StartNewGovInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_gov_internship_accreditation.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:hospital_details", kwargs={"id": self.object.id})
    def get_initial(self):   
        return {
            'hospital_name': self.kwargs["pk"],        
        }
    #def get_form_kwargs(self):
        #self.license = License.objects.get(pk=self.kwargs['pk'])
        #kwargs = super().get_form_kwargs()
        #kwargs['initial']['hospital_name'] = self.license.hospital_name
        #kwargs['initial']['application_no'] = self.license.application_no
        #return kwargs
    def get_queryset(self):
        #hospital = Hospital.objects.filter(hospital_admin=self.request.user)
        return Document.objects.filter(hospital_name__hospital_admin=self.request.user) 
    def get_context_data(self, **kwargs):
        context = super(StartNewGovInternshipRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

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
        return self.render_to_response(self.get_context_data())


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
        return self.render_to_response(self.get_context_data())

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
        return self.render_to_response(self.get_context_data())

class StartPriInternshipRenewal(LoginRequiredMixin, HospitalObjectMixin, SuccessMessageMixin, CreateView):
    model = Document
    template_name = 'hospitals/renew_pri_internship_accreditation.html'
    form_class = HospitalDetailModelForm
    def get_success_url(self):
        return reverse("hospitals:private_hospital_details", kwargs={"id": self.object.id})
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
        context = super(StartPriInternshipRenewal, self).get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

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
        return self.render_to_response(self.get_context_data())


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
        return self.render_to_response(self.get_context_data())


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
                     to_email, fail_silently=True)

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
                     to_email, fail_silently=True)
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
                     to_email, fail_silently=True)

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


class GenerateAccreditationPaymentDetails(LoginRequiredMixin, DetailView):
    template_name = "hospitals/generate_gov_accreditation_invoice.html"
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
        obj = super(GenerateAccreditationPaymentDetails, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        #obj['license_history_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user)
        return obj 


class PayAccreditationFee(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/pay_accreditation_fee.html'
    form_class = PaymentDetailsModelForm
    def get_success_url(self):
        return reverse("hospitals:payment_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name=self.document.hospital_name)
        #context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Radiography Practice')
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
        return self.render_to_response(self.get_context_data())

class PaymentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    template_name = 'hospitals/payment_processing.html'
    form_class = PaymentDetailsModelForm
    def get_success_url(self):
        return reverse("hospitals:payment_details", kwargs={"id": self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_qs'] = Document.objects.select_related("hospital_name").filter(hospital_name=self.document.hospital_name)
        #context['schedule_qs'] = Schedule.objects.select_related("hospital_name").filter(application_status=4, hospital_name=self.schedule.hospital_name, hospital__license_type = 'Radiography Practice')
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
        return self.render_to_response(self.get_context_data())



 
class StartLicenseRenewal(LoginRequiredMixin, DetailView):
    template_name = "hospitals/start_renewal.html"
    model = License
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        return context


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
        return self.render_to_response(self.get_context_data())


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
                     to_email, fail_silently=True)

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
                     to_email, fail_silently=True)

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


class PracticePermitRenewalFinalApproval(LoginRequiredMixin, DetailView):
    template_name = "hospitals/practice_permit_renewal_final_approval.html"
    model = Payment
    
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



class MyLicenseApplicationsHistory(LoginRequiredMixin, ListView):
    template_name = "hospitals/my_license_history.html"
    context_object_name = 'object'

    def get_queryset(self):
        return License.objects.filter(hospital_name__hospital_admin=self.request.user)
    def get_context_data(self, **kwargs):
        obj = super(MyLicenseApplicationsHistory, self).get_context_data(**kwargs)
        obj['hospital_qs'] = Hospital.objects.select_related("hospital_admin").filter(hospital_admin=self.request.user)
        obj['permit_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Radiography Practice Permit')
        #obj['permit_qs'] = License.objects.all()
        obj['certificate_qs'] = License.objects.select_related("hospital_name").filter(hospital_name__hospital_admin=self.request.user, hospital__license_type = 'Internship Accreditation')
        return obj  



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


def download_rad_cert_reg(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=(A4))
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
    p.drawCentredString(421, 380, 'Accreditation Certificate')
    p.setFont("Helvetica", 18, leading=None)
    p.drawCentredString(421, 350, 'This is to certify that')
    p.setFont("Helvetica", 21, leading=None)
    p.drawCentredString(421, 315, str(object.hospital_name))
    p.setFont("Helvetica", 13, leading=None)
    p.drawCentredString(421, 295, str(object.hospital.facility_address))
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 258, 'having satisfied all laid down conditions by Radiographers Registration Board of Nigeria')
    p.setFont("Helvetica", 16, leading=None)
    p.drawCentredString(421, 240, 'for accreditation of hospital/centre for training of Intern Radiographers')
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
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='accreditation_certificate.pdf')   



@login_required
def lookup(request):
   registration = Registration.objects.all()

   context = {
     'registration': registration
   }
   return render(request, 'hospitals/hospitals_lookup.html', context)


