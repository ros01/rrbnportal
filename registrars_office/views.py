from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import registrar_required
from hospitals.models import Payment, Document, Schedule, Inspection, License, Appraisal
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
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib import messages
from xhtml2pdf import pisa
import os
from django.contrib.staticfiles import finders
from io import BytesIO
from django.utils.decorators import method_decorator

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
@registrar_required  
def index(request):
    return render (request, 'registrars_office/registrar_dashboard.html')

class LicenseApprovalListView(LoginRequiredMixin, ListView):
    template_name = "registrars_office/license_approval_list.html"
    context_object_name = 'object'
    

    def get_queryset(self):
        return Inspection.objects.all()


    def get_context_data(self, **kwargs):
        obj = super(LicenseApprovalListView, self).get_context_data(**kwargs)
        obj['approval_list_qs'] = Inspection.objects.filter(inspection_status=2)
        obj['approval_list_qss'] = Appraisal.objects.filter(appraisal_status=2)
        return obj
        
 

class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class LicenseApprovalDetailView(LoginRequiredMixin, InspectionObjectMixin, View):
    template_name = "registrars_office/license_detail.html" # DetailView
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


class InternshipLicenseApprovalDetailView(LoginRequiredMixin, AccreditationObjectMixin, View):
    template_name = "registrars_office/license_appraisal_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)  


def validate(request, id):
  inspection = get_object_or_404(Inspection, pk=id)
  
  context={'inspection': inspection,
           
           }
  return render(request, 'registrars_office/license_detail.html', context)

def approve_license(request, id):
  if request.method == 'POST':
     object = get_object_or_404(Inspection, pk=id)
     object.inspection_status = 4
     object.application_status = 7
     object.save()


     context = {}
     context['object'] = object
     subject = 'Radiography Practise License Approval'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.hospital_name.hospital_admin]
     

     
     contact_message = get_template('registrars_office/license_approved.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

     messages.success(request, ('Radiography Practise License Approval'))
     
     return render(request, 'registrars_office/license_approved.html',context)
    
def approve_internship_license(request, id):
  if request.method == 'POST':
     object = get_object_or_404(Appraisal, pk=id)
     object.appraisal_status = 4
     object.application_status = 7
     object.save()


     context = {}
     context['object'] = object
     subject = 'Radiography Internship License Approval'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.hospital_name.hospital_admin]
     

     
     contact_message = get_template('registrars_office/internship_license_approved.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

     messages.success(request, ('Radiography Internship License Approval'))
     
     return render(request, 'registrars_office/internship_license_approved.html',context)
    

def reject_license(request, id):
  if request.method == 'POST':
     object = get_object_or_404(Inspection, pk=id)
     object.inspection_status = 5
     object.save()

     context = {}
     context['object'] = object
     subject = 'Radiography License Approval Issues'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.hospital_name.hospital_admin]
     

     
     contact_message = get_template('registrars_office/license_rejected.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

     messages.error(request, ('License Approval Issues.  Hospital will be contacted and guided on how to correct application errors.'))
     return render(request, 'registrars_office/license_rejected.html',context)

def reject_internship_license(request, id):
  if request.method == 'POST':
     object = get_object_or_404(Appraisal, pk=id)
     object.appraisal_status = 5
     object.save()

     context = {}
     context['object'] = object
     subject = 'Radiography Internship License Approval Issues'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.hospital_name.hospital_admin]
     

     
     contact_message = get_template('registrars_office/internship_license_rejected.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

     messages.error(request, ('License Approval Issues.  Hospital will be contacted and guided on how to correct application errors.'))
     return render(request, 'registrars_office/internship_license_rejected.html',context)


def validate_report(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  
  context={'appraisal': appraisal,
           
           }
  return render(request, 'registrars_office/license_appraisal_detail.html', context)















#class InspectionReportsView(LoginRequiredMixin, View):
    #template_name = "registrars_office/inspection_reports_list.html"
    #queryset = Inspection.objects.all()

    #def get_queryset(self):
        #return self.queryset
        #return self.queryset
        

    #def get(self, request, *args, **kwargs):
        #context = {'object': self.get_queryset()}
        #return render(request, self.template_name, context)


class InspectionReportsView(LoginRequiredMixin, ListView):
    template_name = 'registrars_office/inspection_reports_list.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Inspection.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(InspectionReportsView, self).get_context_data(**kwargs)

        obj['inspection_qs'] = Inspection.objects.filter(inspection_status=1)
        obj['inspections_qs'] = Inspection.objects.all()
        obj['appraisal_qs'] = Appraisal.objects.filter(appraisal_status=1)
        obj['appraisals_qs'] = Appraisal.objects.all()
        
        return obj


def view_inspection_report(request, id):
  inspection = get_object_or_404(Inspection, pk=id)
  
  context={'inspection': inspection,
           
           }
  return render(request, 'registrars_office/inspection_details.html', context)


def view_appraisal_report(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  
  context={'appraisal': appraisal,
           
           }
  return render(request, 'registrars_office/appraisal_details.html', context)




class IssuedLicensesListView(LoginRequiredMixin, View):
    template_name = "registrars_office/issued_licenses_list.html"
    queryset = License.objects.all().order_by('-issue_date')
   

    def get_queryset(self):
        return self.queryset        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

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


class LicensePdfView(LoginRequiredMixin, GenerateObjectMixin, View):
    
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

class RegisteredHospitalsListView(LoginRequiredMixin, View):
    template_name = "registrars_office/registered_hospitals_list.html"
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
    template_name = "registrars_office/hospital_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

