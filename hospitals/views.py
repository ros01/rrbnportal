from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.views import View
from .forms import BasicDetailModelForm, CertUploadModelForm, PaymentDetailsModelForm, ReceiptUploadModelForm
from django.urls import reverse, reverse_lazy
from django.template.loader import get_template
from django.conf import settings
from . import views
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView
)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from .models import Registration, Payment, Inspection, License, Schedule
from django.db.models import Q  
from xhtml2pdf import pisa
import os
from django.contrib.staticfiles import finders
from io import BytesIO



User = get_user_model()


def hospitals_dashboard(request):
     return render(request, 'hospitals/hospitals_dashboard.html')


def status(request, *args, **kwargs):
    has_license = License.objects.filter(practice_manager=request.user)
    has_inspection = Inspection.objects.filter(practice_manager=request.user)
    has_schedule = Schedule.objects.filter(practice_manager=request.user)
    has_payment = Payment.objects.filter(practice_manager=request.user)
    has_registeration = Registration.objects.filter(practice_manager=request.user)
   
    if has_license:
        return redirect('hospitals:licenses_list')
    elif has_inspection:
        return redirect('hospitals:inspection_table')
    elif has_schedule:
        return redirect('hospitals:schedule_table')
    elif has_payment:
        return redirect('hospitals:payment_verified_table')
    elif has_registeration:
        return redirect('hospitals:payment_table') 
    else:
        return redirect('hospitals:reg_table')
    

def reg_table(request):
     return render(request, 'hospitals/reg_table.html')


class HospitalCreateView(CreateView):
    template_name = 'hospitals/hospitals_register.html'
    form_class = BasicDetailModelForm
    queryset = Registration.objects.all()
    

class HospitalUpdateView(View):
    template_name = 'hospitals/hospitals_validate.html'
    template_name1 = 'hospitals/hospitals_reg_confirmation.html'
    queryset = Registration.objects.all()

    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(Registration, id=id)

        return obj

    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = CertUploadModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
           form = CertUploadModelForm(
               request.POST, request.FILES, instance=obj)
           if form.is_valid():
              form.save()
           context['object'] = obj
           context['form'] = form

           subject = 'Acknowledgment of Interest to Register with RRBN'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [obj.email]

           context['form'] = form
           contact_message = get_template(
               'hospitals/contact_message.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)

        return render(request, self.template_name1, context)

class PaymentListView(View):
    template_name = "hospitals/payment_table.html"
    queryset = Registration.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)
        

class PaymentObjectMixin(object):
    model = Registration
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class PaymentCreateView(PaymentObjectMixin, View):
    template_name = "hospitals/payment_processing.html"
    template_name1 = 'hospitals/payment_details_submission.html'
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

           subject = 'Receipt of Registration Fee Payment Details'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [request.user.email]

           context['form'] = form
           contact_message = get_template(
               'hospitals/payment_message.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)  
        
        return render(request, self.template_name1, context)

class PaymentUpdateView(View):
    template_name = 'hospitals/check_payment_details.html'
    template_name1 = 'hospitals/payment_details_submission.html'
    queryset = Payment.objects.all()

    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(Payment, id=id)
        return obj

    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = ReceiptUploadModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
           form = ReceiptUploadModelForm(request.POST, request.FILES, instance=obj)
           if form.is_valid():
              form.save()
           context['object'] = obj
           context['form'] = form

           subject = 'Receipt of Registration Fee Payment Details'
           from_email = settings.DEFAULT_FROM_EMAIL
           to_email = [request.user.email]

           context['form'] = form
           contact_message = get_template(
               'hospitals/payment_message.txt').render(context)

           send_mail(subject, contact_message, from_email,
                     to_email, fail_silently=False)
        return render(request, self.template_name1, context)


class PaymentVerificationListView(View):
    template_name = "hospitals/payment_verification_table.html"
    queryset = Payment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class PaymentObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class PaymentVerificationDetailView(PaymentObjectMixin, View):
    template_name = "hospitals/payment_verification_details.html" 
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class ScheduleListView(View):
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


class ScheduleDetailView(ScheduleObjectMixin, View):
    template_name = "hospitals/inspection_schedule_details.html" 
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class InspectionListView(View):
    template_name = "hospitals/inspection_report_table.html"
    queryset = Inspection.objects.all()

    def get_queryset(self):
        #return self.queryset.filter(inspection_status=2)
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)

class InspectionObjectMixin(object):
    model = Inspection
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionView(InspectionObjectMixin, View):
    template_name = "hospitals/inspection_report_detail.html" 
    def get(self, request, id=None, *args, **kwargs):
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)




class MyLicensesListView(View):
    template_name = "hospitals/my_license_table.html"
    queryset = License.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)
        

    def get(self, request, *args, **kwargs):
        context = {'object': self.get_queryset()}
        return render(request, self.template_name, context)


class LicenseObjectMixin(object):
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



class MyLicensesDetailView(LicenseObjectMixin, View):
    
    def get(self, request, *args, **kwargs):
        template = get_template('pdf/license.html')
        context = {
            'object': self.get_object()
        }
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result, link_callback=link_callback)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf') 
        return None







@login_required
def lookup(request):
   registration = Registration.objects.all()

   context = {
     'registration': registration
   }
   return render(request, 'hospitals/hospitals_lookup.html', context)


