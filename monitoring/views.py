from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from accounts.decorators import monitoring_required
from hospitals.models import Payment, Registration
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

User = get_user_model()



@login_required
@monitoring_required
def monitoring_dashboard(request):
    return render(request, 'monitoring/monitoring_dashboard.html')


#class PaymentsView(View):
   # template_name = 'monitoring/list-applications.html'
   # queryset = Registration.objects.all()

    #def get_queryset(self):
       # return self.queryset


    #def get(self, request, *args, **kwargs):
       # context = {'object_list': self.get_queryset()}
       # return render(request, self.template_name, context)


def registration_list(request):
  payment = Payment.objects.all()
  
  context={'payment': payment,
           
           }
  return render(request, 'monitoring/list-applications.html', context)


#class RegVerifyView(View):
  #  template_name = 'monitoring/view-applications.html'
  #  queryset = Registration.objects.all()

    #def get_queryset(self):
      #  return self.queryset


   # def get(self, request, *args, **kwargs):
       # context = {'registration': self.get_queryset()}
      #  return render(request, self.template_name, context)

class InspectionObjectMixin(object):
    model = Payment
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class InspectionView(InspectionObjectMixin, View):
    template_name = "hospitals/inspection_detail.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)


class InspectionListView(View):
    template_name = "hospitals/inspection_table.html"
    queryset = Payment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(practice_manager=self.request.user)

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)

class InspectionCreateView(View):
    template_name = "monitoring/schedule_inspection.html" # DetailView
    def get(self, request, *args, **kwargs):
        # GET method
        form = InspectionModelForm()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # POST method
        form = InspectionModelForm(request.POST)
        if form.is_valid():
            form.save()
            form = InspectionModelForm()
        context = {"form": form}
        return render(request, self.template_name, context)








@login_required
def vet_application(request, id):
  payment = get_object_or_404(Payment, pk=id)
  
  context={'payment': payment,
           
           }
  return render(request, 'monitoring/view-applications.html', context)


def approve(request, id):
  if request.method == 'POST':
     payment = get_object_or_404(Payment, pk=id)
     payment.vet_status = 2
     payment.save()


     context = {}
     context['object'] = payment
     subject = 'Successful verification of Registration and Payment Details'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [payment.email]
     

     
     contact_message = get_template('monitoring/contact_message.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

     messages.success(request, ('Application vetted successfully. Please proceed to Schedule Hospital for Inspection.'))
     #return redirect('/monitoring/'+str(payment.id))
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
     




