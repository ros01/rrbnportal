from django import forms
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Inspection
from .choices import STATE_CHOICES, SERVICES, EQUIPMENT, PAYMENT_METHOD




class InspectionModelForm(forms.ModelForm):
    state = forms.ChoiceField(choices = STATE_CHOICES, widget=forms.Select(), required=True)
    services = forms.ChoiceField(choices = SERVICES, widget=forms.Select(), required=True)
    equipment = forms.MultipleChoiceField(choices = EQUIPMENT, widget=forms.CheckboxSelectMultiple())

    class Meta:
         model = Inspection
         fields = ('practice_manager','hospital_name', 'license_category', 'rc_number', 'phone', 'email',  'city', 'state', 'address', 'services', 'equipment', 'radiographers')
         

         widgets = {'practice_manager': forms.HiddenInput(),}

    