from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .choices import * 

from captcha.fields import CaptchaField, CaptchaTextInput
from hospitals.models import License
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from django.contrib.auth import get_user_model
User = get_user_model()


class SignupForm(UserCreationForm):
    hospital_type = forms.ChoiceField(choices = HOSPITAL_TYPE, widget=forms.Select(), required=True)


    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_no', 'hospital_name', 'password1', 'password2',  'hospital_type')



    def __init__(self, *args, **kwargs):
       super(SignupForm, self).__init__(*args, **kwargs)
       self.fields['first_name'].label = "First Name"
       self.fields['last_name'].label = "Last Name"
       self.fields['phone_no'].label = "Phone Number"
       self.fields['hospital_name'].label = "Hospital Name"
       self.fields['hospital_type'].label = "Application Type"
       


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



    



