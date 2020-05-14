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
from .models import Registration, Payment, Inspection, License
from django.db.models import Q  



User = get_user_model()



@login_required
def hospitals_dashboard(request):
    return render(request, 'hospitals/hospitals_dashboard.html')


@login_required
def lookup(request):
   registration = Registration.objects.all()

   context = {
     'registration': registration
   }
   return render(request, 'hospitals/hospitals_lookup.html', context)


@login_required
def status(request, *args, **kwargs):
    has_license = License.objects.filter(practice_manager=request.user)
    has_inspected = Inspection.objects.filter(practice_manager=request.user)
    has_paid = Payment.objects.filter(practice_manager=request.user)
    has_registered = Registration.objects.filter(practice_manager=request.user)
    

    if has_inspected:
        return redirect('hospitals:license_table')
    elif has_paid:
        return redirect('hospitals:inspection_table')
    elif has_registered:
        return redirect('hospitals:payment_table') 
    else:
        return redirect('hospitals:reg_table')
    

@login_required
def reg_table(request):
     return render(request, 'hospitals/reg_table.html')

@login_required
def inspection_table(request):
     return render(request, 'hospitals/inspection_table.html')


@login_required
def license_table(request):
     return render(request, 'hospitals/license_table.html')



class PaymentListView(View):
    template_name = "hospitals/payment_table.html"
    queryset = Registration.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)



class  PaymentCreateView(CreateView):
    template_name = "hospitals/payment_processing.html" 
    form_class = PaymentDetailsModelForm

  
 
    def get_initial(self, *args, **kwargs):
        initial = super(PaymentCreateView, self).get_initial(**kwargs)
        initial['application_no'] = get_object_or_404(Registration, id = self.kwargs.get('id'))

        return initial
    
    

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
           form = ReceiptUploadModelForm(
               request.POST, request.FILES, instance=obj)
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



