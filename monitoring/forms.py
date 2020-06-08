from django import forms
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Schedule, Inspection, License
from tempus_dominus.widgets import DatePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from hospitals.choices import INSPECTION_ZONE, LICENSE_STATUS
from django.conf import settings



class ScheduleModelForm(forms.ModelForm):
    inspection_date = forms.DateField(
    	widget=DatePicker(
    		options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                'maxDate': '2025-12-31',
            },
    		attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
                }
                )
    	)

    inspection_report_deadline = forms.DateField(
    	widget=DatePicker(
    		options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                'maxDate': '2025-12-31',
            },
    		attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
                }
                )
    	)
    inspection_zone = forms.ChoiceField(choices = INSPECTION_ZONE, widget=forms.Select(), required=True)

    

    class Meta:
        model = Schedule
        fields = ('application_no', 'practice_manager', 'hospital_name', 'license_category', 'phone', 'email', 'address', 'state', 'city', 'services', 'equipment', 'radiographers', 'inspection_date', 'inspection_report_deadline', 'inspection_zone',)
        widgets = {'application_no': forms.HiddenInput(), 'practice_manager': forms.HiddenInput(), 'hospital_name': forms.HiddenInput(), 'license_category': forms.HiddenInput(), 'phone': forms.HiddenInput(), 'email': forms.HiddenInput(), 'address': forms.HiddenInput(), 'state': forms.HiddenInput(), 'city': forms.HiddenInput(),  'services': forms.HiddenInput(), 'equipment': forms.HiddenInput(), 'radiographers': forms.HiddenInput(),}



    def __init__(self, *args, **kwargs):
       super(ScheduleModelForm, self).__init__(*args, **kwargs)
       self.fields['inspection_zone'].label = False
       self.fields['inspection_date'].label = "Inspection Date"
       self.fields['inspection_report_deadline'].label = "Inspection Report Deadline"



class LicenseModelForm(forms.ModelForm):
    issue_date = forms.DateField(
        widget=DatePicker(
            options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                'maxDate': '2025-12-31',
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
                }
                )
        )

    expiry_date = forms.DateField(
        widget=DatePicker(
            options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                'maxDate': '2025-12-31',
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
                }
                )
        )
    license_status = forms.ChoiceField(choices = LICENSE_STATUS, widget=forms.Select(), required=True)

    

    class Meta:
        model = License
        fields = ('application_no', 'practice_manager', 'hospital_name', 'license_category', 'address', 'phone', 'email', 'inspection_date', 'issue_date', 'expiry_date', 'license_status', 'license_no',)
        widgets = {'application_no': forms.HiddenInput(), 'practice_manager': forms.HiddenInput(), 'hospital_name': forms.HiddenInput(), 'license_category': forms.HiddenInput(), 'address': forms.HiddenInput(), 'phone': forms.HiddenInput(), 'email': forms.HiddenInput(), 'inspection_date': forms.HiddenInput(),}



    def __init__(self, *args, **kwargs):
       super(LicenseModelForm, self).__init__(*args, **kwargs)
       self.fields['issue_date'].label = "Issue Date"
       self.fields['expiry_date'].label = "Expiry Date"
    
    
      
     



        



    


		


