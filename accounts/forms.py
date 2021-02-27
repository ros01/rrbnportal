from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .choices import * 

from captcha.fields import CaptchaField, CaptchaTextInput
from hospitals.models import License
from .models import Hospital
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from django.contrib.auth import get_user_model
User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'hospital', 'type')



    def __init__(self, *args, **kwargs):
       super(SignupForm, self).__init__(*args, **kwargs)
       self.fields['first_name'].label = "First Name"
       self.fields['last_name'].label = "Last Name"
       self.fields['email'].label = "Email Address"
       self.fields['email'].widget.attrs['placeholder'] = "enter Email Address"
       #self.fields['application_type'].label = "Application Type"
       #self.fields['application_type'].widget.attrs['placeholder'] = "Select Application Type"
       
class HospitalModelForm(forms.ModelForm):
      
    class Meta:
         model = Hospital
         fields = ('hospital_name', 'rc_number', 'phone_no', 'state', 'city', 'address')
         

         widgets = {
            'address': forms.Textarea(attrs={'rows':2, 'cols':3}),   
            }

    def __init__(self, *args, **kwargs):
       super(HospitalModelForm, self).__init__(*args, **kwargs)
       self.fields['hospital_name'].label = "Hospital Name"
       self.fields['hospital_name'].widget.attrs['placeholder'] = "enter Hospital Name"
       self.fields['rc_number'].label = "RC Number"
       self.fields['rc_number'].widget.attrs['placeholder'] = "leave Blank if unavailable"
       self.fields['phone_no'].label = "Mobile Telephone Number"
       self.fields['phone_no'].widget.attrs['placeholder'] = "enter GSM Number"
       self.fields['state'].label = "State of Location"
       self.fields['state'].widget.attrs['placeholder'] = "enter State of Location"
       self.fields['city'].label = "City of Location"
       self.fields['city'].widget.attrs['placeholder'] = "Enter City of Location"
       self.fields['address'].label = "Address"
       self.fields['address'].widget.attrs['placeholder'] = "Enter Address"
       
        


class RenewalModelForm(forms.ModelForm):
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = License
        fields=('license_no', 'captcha')


    def __init__(self, *args, **kwargs):
       super(RenewalModelForm, self).__init__(*args, **kwargs)
       self.fields['license_no'].label = "License Number"
       self.fields['license_no'].widget.attrs['placeholder'] = "Enter License Number"
       self.fields['captcha'].label = "Text Verification"
       self.fields['captcha'].widget.attrs['placeholder'] = "Enter Captcha"



    



