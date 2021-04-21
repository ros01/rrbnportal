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

from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.pagesizes import landscape, portrait
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
@registrar_required  
def index(request):
    return render (request, 'registrars_office/registrar_dashboard.html')


class MyUserAccount(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registrars_office/my_profile.html')

class InternshipCertificateList(LoginRequiredMixin, ListView):
    template_name = "registrars_office/internship_certificate_approval_list.html"
    context_object_name = 'object'

    def get_queryset(self):
        return Appraisal.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(InternshipCertificateList, self).get_context_data(**kwargs)
        obj['internship_certificate_qs'] = Appraisal.objects.filter(appraisal_status=2)
        return obj

class NewPracticePermitList(LoginRequiredMixin, ListView):
    template_name = "registrars_office/new_practice_permit_approval_list.html"
    context_object_name = 'object'
    
    def get_queryset(self):
        return Inspection.objects.all()

    def get_context_data(self, **kwargs):
        obj = super(NewPracticePermitList, self).get_context_data(**kwargs)
        obj['new_practice_permit_qs'] = Inspection.objects.filter(inspection_status=2)
        return obj

class PracticePermitRenewalList(LoginRequiredMixin, ListView):
    template_name = "registrars_office/practice_permit_renewals_list.html"
    context_object_name = 'object'
    
    def get_queryset(self):
        return Payment.objects.all()


    def get_context_data(self, **kwargs):
        obj = super(PracticePermitRenewalList, self).get_context_data(**kwargs)
        obj['practice_permit_renewals_qs'] = Payment.objects.select_related("hospital_name").filter(application_status=3, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        return obj



class LicenseApprovalListView(LoginRequiredMixin, ListView):
    template_name = "registrars_office/license_approval_list.html"
    context_object_name = 'object'
    

    def get_queryset(self):
        return Inspection.objects.all()


    def get_context_data(self, **kwargs):
        obj = super(LicenseApprovalListView, self).get_context_data(**kwargs)
        obj['renewal_qs'] = Payment.objects.select_related("hospital_name").filter(vet_status=2, hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'Renewal - Radiography Practice Permit')
        obj['approval_list_qs'] = Inspection.objects.filter(inspection_status=2)
        obj['approval_list_qss'] = Appraisal.objects.filter(appraisal_status=2)
        return obj
        
 
class PaymentObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class PracticePermitRenewalAppDetails(LoginRequiredMixin, PaymentObjectMixin, View):
    template_name = "registrars_office/practice_permit_renewal_app_details.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)


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
     subject = 'Radiography Practise Permit Approval'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.hospital_name.hospital_admin]
     

     
     contact_message = get_template('registrars_office/license_approved.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=True)

     messages.success(request, ('Radiography Practise Permit Approval'))
     
     return render(request, 'registrars_office/license_approved.html',context)

def approve_practice_permit_renewal(request, id):
  if request.method == 'POST':
     object = get_object_or_404(Payment, pk=id)
     object.application_status = 7
     object.save()


     context = {}
     context['object'] = object
     subject = 'Radiography Practise Permit Approval'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [object.hospital_name.hospital_admin]
     

     
     contact_message = get_template('registrars_office/practice_permit_approved.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=True)

     messages.success(request, ('Radiography Practise Permit Renewal Approval'))
     
     return render(request, 'registrars_office/practice_permit_approved.html',context)
    
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

     send_mail(subject, contact_message, from_email, to_email, fail_silently=True)

     messages.success(request, ('Radiography Internship Accreditation Approval'))
     
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

     send_mail(subject, contact_message, from_email, to_email, fail_silently=True)

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

     send_mail(subject, contact_message, from_email, to_email, fail_silently=True)

     messages.error(request, ('License Approval Issues.  Hospital will be contacted and guided on how to correct application errors.'))
     return render(request, 'registrars_office/internship_license_rejected.html',context)


def validate_report(request, id):
  appraisal = get_object_or_404(Appraisal, pk=id)
  
  context={'appraisal': appraisal,
           
           }
  return render(request, 'registrars_office/license_appraisal_detail.html', context)



class RadRegCerttificateListView(LoginRequiredMixin, ListView):
    template_name = "registrars_office/radiography_reg_cert_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(RadRegCerttificateListView, self).get_context_data(**kwargs)
        obj['rad_cert_reg'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit', hospital__application_type = 'New Registration - Radiography Practice Permit').order_by('-issue_date')
        return obj    


class RadPracticePermitListView(LoginRequiredMixin, ListView):
    template_name = "registrars_office/rad_practice_permit_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(RadPracticePermitListView, self).get_context_data(**kwargs)
        obj['rad_practice_permit'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Radiography Practice Permit').order_by('-issue_date')
        return obj  


class AccreditationCertificateListView(LoginRequiredMixin, ListView):
    template_name = "registrars_office/accreditation_cert_list.html"
    context_object_name = 'object'   
    def get_queryset(self):
        return License.objects.all()  
    def get_context_data(self, **kwargs):
        obj = super(AccreditationCertificateListView, self).get_context_data(**kwargs)
        obj['accreditation_cert'] = License.objects.select_related("hospital_name").filter(hospital__license_type = 'Internship Accreditation').order_by('-issue_date')   
        return obj  



def download_rad_cert_reg(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=(A4))
    object = get_object_or_404(License, pk=id)

    image_path1 = '%s/img/cert_border1.jpeg' % settings.STATIC_ROOT
    image_path2 = '%s/img/logo_small.png' % settings.STATIC_ROOT
    image_path3 = '%s/img/cert_seal4.jpeg' % settings.STATIC_ROOT
    image_path4 = '%s/img/reg_sign.jpg' % settings.STATIC_ROOT
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

    p.setFont("Helvetica", 16, leading=None)
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
    image_path4 = '%s/img/reg_sign.jpg' % settings.STATIC_ROOT
    #image_path5 = '%s/img/passport.jpg' % settings.STATIC_ROOT
    p.drawImage(image_path1, 0, 0, width=595, height=840)

    p.drawImage(image_path2, 150, 550, width=115, height=115)

  # Header Text
    p.setFont("Helvetica-Bold", 16, leading=None)
    p.drawCentredString(300, 780, 'THE RADIOGRAPHERS REGISTRATION BOARD OF NIGERIA')

  # Body Text
    p.setFont("Helvetica", 12, leading=None)
    p.drawCentredString(300, 765, 'Established by Decree 42, 1987 (now Cap R1 LFN 2004)')

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
    image_path4 = '%s/img/reg_sign.jpg' % settings.STATIC_ROOT
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











#class InspectionReportsView(LoginRequiredMixin, View):
    #template_name = "registrars_office/inspection_reports_list.html"
    #queryset = Inspection.objects.all()

    #def get_queryset(self):
        #return self.queryset
        #return self.queryset
        

    #def get(self, request, *args, **kwargs):
        #context = {'object': self.get_queryset()}
        #return render(request, self.template_name, context)


class InspectionCompletedListView(LoginRequiredMixin, ListView):
    template_name = 'registrars_office/inspections_completed_list.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Inspection.objects.all()
    def get_context_data(self, **kwargs):
        obj = super(InspectionCompletedListView, self).get_context_data(**kwargs)
        obj['inspection_qs'] = Inspection.objects.select_related("hospital_name").filter(vet_status=4)
        obj['appraisal_qs'] = Appraisal.objects.select_related("hospital_name").filter(vet_status=4)
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
    template_name = "registrars_office/inspections_detail.html" # DetailView
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
    template_name = "registrars_office/appraisals_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        #context = {'object': self.get_object()}
        return render(request, self.template_name, context)





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

