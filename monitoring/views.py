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
  registration = Registration.objects.all()
  
  context={'registration': registration,
           
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






def vet_application(request, id):
  registration = get_object_or_404(Registration, pk=id)
  
  context={'registration': registration,
           
           }
  return render(request, 'monitoring/view-applications.html', context)


def approve(request, id):
  if request.method == 'POST':
     registration = get_object_or_404(Registration, pk=id)
     registration.vet_status = 2
     registration.save()


     context = {}
     context['object'] = registration
     subject = 'Successful verification of Registration and Payment Details'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [registration.email]
     

     
     contact_message = get_template('monitoring/contact_message.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

     messages.success(request, ('Application vetted successfully. Please proceed to Schedule Hospital for Inspection.'))
     return redirect('/monitoring/'+str(registration.id))
     


def reject(request, id):
  if request.method == 'POST':
     registration = get_object_or_404(Registration, pk=id)
     registration.vet_status = 3
     registration.save()

     context = {}
     context['object'] = registration
     subject = 'Failed verification of Registration and Payment Details'
     from_email = settings.DEFAULT_FROM_EMAIL
     to_email = [registration.email]
     

     
     contact_message = get_template('monitoring/verification_failed.txt').render(context)

     send_mail(subject, contact_message, from_email, to_email, fail_silently=False)





     messages.error(request, ('Verification failed.  Hospital has been sent an email to re-apply with the correct details.'))
     return redirect('/monitoring/'+str(registration.id))
     




