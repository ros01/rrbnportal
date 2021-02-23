from django.views import View
from django.http import HttpResponse
from .models import Hospital
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .forms import SignupForm, RenewalModelForm, HospitalModelForm
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.http import HttpResponse, Http404
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model, update_session_auth_hash, authenticate, login as auth_login
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth import views as auth_views
from django.views.generic import DetailView, TemplateView, ListView
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.tokens import account_activation_token
from django.contrib import messages, auth
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from hospitals.models import License
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView
)

from django.core.exceptions import ObjectDoesNotExist



AUTH_USER_MODEL = 'accounts.User'

User = get_user_model()

class StartView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/reg-start-details.html')

class LoginTemplateView(TemplateView):
    template_name = "accounts/login.html"


def activate_account(request):
    return render(request, 'accounts/activate_account.html')


#def CreateHospitalProfile(request):
    #if request.method == 'POST':
        #user_form = SignupForm(request.POST)
        #hospital_form = HospitalModelForm(request.POST)
        
        #if user_form.is_valid and hospital_form.is_valid:
            #user = user_form.save(commit=False)
            #user.is_active = False  # Deactivate account till it is confirmed
            #user.save()
            #hospital = hospital_form.save(commit=False)
            #Hospital.objects.create(
                #hospital_admin = user,
                #hospital_name = hospital.hospital_name,
                #rc_number = hospital.rc_number,
                #phone_no = hospital.phone_no,
                #state = hospital.state,
                #city = hospital.city,
                #hospital_type = hospital.hospital_type,
                #)
            
        #current_site = get_current_site(request)
        #subject = 'Activate Your RRBN Portal Account'
        #from_email = settings.DEFAULT_FROM_EMAIL
        #to_email = [user.email]
        #message = render_to_string('accounts/activation_request.html', {
            #'user': user,
            #'hospital': hospital,
            #'domain': current_site.domain,
            #'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #'token': account_activation_token.make_token(user),
        #})
        #send_mail(subject, message, from_email, to_email, fail_silently=False)

        #messages.success(request, ('Please Confirm your email to complete registration.'))

        #return render(request, 'accounts/profile-creation-confirmation.html')
    
    #user_form = SignupForm()
    #hospital_form = HospitalModelForm()        

    #return render(request, "accounts/profile_creation.html", {'user_form':user_form, 'hospital_form':hospital_form,})
     
class CreateHospitalProfile(View):
    user_form = SignupForm
    hospital_form = HospitalModelForm
    template_name = 'accounts/profile_creation.html'
    template_name1 = 'accounts/profile-creation-confirmation.html'
 
    def get(self, request, *args, **kwargs):
        user_form = self.user_form()
        hospital_form = self.hospital_form()
        return render(request, self.template_name, {'user_form':user_form, 'hospital_form':hospital_form,})
    def post(self, request, *args, **kwargs):
        user_form = self.user_form(request.POST)
        hospital_form = self.hospital_form(request.POST)

        if user_form.is_valid() and hospital_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            hospital = hospital_form.save(commit=False)
            Hospital.objects.create(
                hospital_admin = user,
                license_type = user.license_type,
                hospital_name = hospital.hospital_name,
                rc_number = hospital.rc_number,
                phone_no = hospital.phone_no,
                state = hospital.state,
                city = hospital.city,
                address = hospital.address,
               
                )
            
            current_site = get_current_site(request)
            subject = 'Activate Your RRBN Portal Account'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user.email]
            message = render_to_string('accounts/activation_request.html', {
                'user': user,
                'hospital': hospital,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            messages.success(request, ('Please Confirm your email to complete registration.'))

            return render(request, self.template_name1)

             

        return render(request, self.template_name, {'user_form':user_form, 'hospital_form':hospital_form,})



#class SignUpView(View):
    #form_class = SignupForm
    #template_name = 'accounts/register.html'
    #template_name1 = 'accounts/profile-creation-confirmation.html'
 
    #def get(self, request, *args, **kwargs):
        #form = self.form_class()
        #return render(request, self.template_name, {'form': form})
    #def post(self, request, *args, **kwargs):
        #form = self.form_class(request.POST)
        #if form.is_valid():
            #user = form.save(commit=False)
            #user.is_active = False  # Deactivate account till it is confirmed
            #user.save()
            #current_site = get_current_site(request)
            #subject = 'Activate Your RRBN Portal Account'
            #from_email = settings.DEFAULT_FROM_EMAIL
            #to_email = [form.cleaned_data.get('email')]
            #message = render_to_string('accounts/activation_request.html', {
                #'user': user,
                #'domain': current_site.domain,
                #'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                #'token': account_activation_token.make_token(user),
           # })
            #send_mail(subject, message, from_email, to_email, fail_silently=False)

            #messages.success(
                #request, ('Please Confirm your email to complete registration.'))

            #return render(request, self.template_name1)
        #else:
            #return render(request, self.template_name, {'form': form})

def renewal(request):
    try:
        query = request.GET.get('q')
        results = 0

    except ValueError:
        query = None
        results = None
    try:
        results = License.objects.get(license_no=query)
    except ObjectDoesNotExist:
        messages.error(request, ('License Number is Invalid.  Enter a Valid License Number'))
        pass

    return render(request, 'accounts/results.html', {"results": results})



class ProfileObjectMixin(object):
    model = User
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class ProfileUpdateView(ProfileObjectMixin, View):
    template_name = "accounts/update_profile.html"
    template_name1 = "accounts/profile_update_confirmation.html"
    
    def get(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = SignupForm(instance=obj)
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
           form = SignupForm(request.POST, instance=obj)
           if form.is_valid():
                user = form.save(commit=False)
                user.is_active = True  
                user.save()
           context['object'] = obj
           context['form'] = form
        
        return render(request, self.template_name1, context)



def delete(request, license_id):
    license = License.objects.get(pk=license_id)
    license.delete()
    messages.success(request, ('License deleted'))
    return redirect('accounts/renewal.html')

class RenewalObjectMixin(object):
    model = License
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 

class RenewalCreateView(CreateView):
    template_name = 'accounts/renewal.html'
    form_class = RenewalModelForm


def profile_details(request, id=id):
    obj = get_object_or_404(User, id=id)
    form = SignupForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
    context = {
        'form': form
    }
    return render(request, "accounts/update_profile.html", context)


class RenewalView(RenewalObjectMixin, View):
    template_name = "accounts/renewal.html"
    template_name1 = "accounts/renewal.html"
    def get(self, request,  *args, **kwargs):
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = RenewaModelForm(instance=obj)  
            context['object'] = obj
            context['form'] = form

        return render(request, self.template_name, context)


    def post(self, request,  *args, **kwargs):
        form = RenewaModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        context = {}
        obj = self.get_object()
        if obj is not None:
          
           context['object'] = obj
           context['form'] = form

           
        
        
        return render(request, self.template_name1, context)

class RenewalView(ListView):
    model = License
    template_name = 'accounts/renewal.html'
    
    def get_queryset(self): 
        query = self.request.GET.get('q')
        object_list = License.objects.filter(
            Q(license_no__iexact=query) | Q(hospital_name__iexact=query)
        )
        return object_list

class SearchResultsView(ListView):
    model = License
    template_name = 'accounts/search_result.html'
    
    def get_queryset(self): 
        query = self.request.GET.get('q')
        object_list = License.objects.filter(
            Q(license_no__iexact=query) | Q(hospital_name__iexact=query)
        )
        return object_list

class RenewalTemplateView(TemplateView):
    template_name = "accounts/renewal.html"
    


def login(request):
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']

    user = auth.authenticate(email=email, password=password)
    if user is not None:
        auth_login(request, user)
        
        if user.license_type == 'Radiography Practice':
            return redirect('hospitals:hospitals_dashboard')
        if user.license_type == 'Internship Accreditation':
            return redirect('hospitals:hospitals_dashboard')
        if user.role == 'Monitoring':
            return redirect('monitoring:monitoring_dashboard')
        if user.role == 'Registrar':
            return redirect('registrars_office:registrar_dashboard')
        if user.role == 'Zonal Offices':
            return redirect('zonal_offices:zonal_offices_dashboard')
        if user.role == 'Finance':
            return redirect('finance:finance_dashboard')
        else:
            messages.error(request, 'Please enter the correct email and password for your account. Note that both fields may be case-sensitive.')
            return redirect('accounts:signin')
    else:
        messages.error(request, 'Please enter the correct email and password for your account. Note that both fields may be case-sensitive.')
        return redirect('accounts:signin')





class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            auth_login(request, user)
            messages.success(request, ('Your account have been confirmed.'))
            return redirect('hospitals:hospitals_dashboard')
        else:
            messages.warning(
                request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('index')


class SignUpView(View):
    form_class = SignupForm
    template_name = 'accounts/register.html'
    template_name1 = 'accounts/profile-creation-confirmation.html'
 
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your RRBN Portal Account'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [form.cleaned_data.get('email')]
            message = render_to_string('accounts/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            messages.success(
                request, ('Please Confirm your email to complete registration.'))

            return render(request, self.template_name1)

        return render(request, self.template_name, {'form': form})



class StartIntershipApplication(View):
    form_class = SignupForm
    template_name = 'accounts/register_internship.html'
    template_name1 = 'accounts/profile-creation-confirmation.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
    
            current_site = get_current_site(request)
            subject = 'Activate Your RRBN Portal Account'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [form.cleaned_data.get('email')]
            message = render_to_string('accounts/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            messages.success(
                request, ('Please Confirm your email to complete registration.'))

            return render(request, self.template_name1)

        return render(request, self.template_name, {'form': form})

class ProfileObjectMixin(object):
    model = settings.AUTH_USER_MODEL
    def get_object(self):
        id = self.kwargs.get('id')
        obj = None
        if id is not None:
            obj = get_object_or_404(self.model, id=id)
        return obj 


class ProfileDetailView(ProfileObjectMixin, View):
    template_name = "accounts/profile-creation-confirmation.html" # DetailView
    def get(self, request, id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object()}
        return render(request, self.template_name, context)

#class ProfileDetailView(DetailView):
    #model = User
   # model = settings.AUTH_USER_MODEL
   # template_name = "accounts/profile-creation-confirmation.html"



class StartReg(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/start-accreditation.html')


def logout(request):
  if request.method == 'POST':
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('index')


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('accounts:password-reset-complete')
    form_valid_message = ("Your password was changed!")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PasswordResetView(auth_views.PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'accounts/password-reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    #subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'accounts/password-reset-email.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password-reset-done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password-reset-confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('accounts:password-reset-complete')
    form_valid_message = ("Your password was changed!")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password-reset-complete.html'

