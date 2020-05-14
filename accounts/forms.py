from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .choices import * 

from django.contrib.auth import get_user_model
User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    phone_no = forms.CharField(max_length=100, help_text='Phone Number')
    hospital_name = forms.CharField(max_length=200, help_text='Hospital Name')
    hospital_type = forms.ChoiceField(choices = HOSPITAL_TYPE, widget=forms.Select(), required=True)


    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_no', 'hospital_name', 'password1', 'password2',  'hospital_type')
