from django import forms
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Schedule, Inspection, License, Records
from tempus_dominus.widgets import DatePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from hospitals.choices import INSPECTION_ZONE, LICENSE_STATUS, STATE_CHOICES, SERVICES, EQUIPMENT
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404




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
        fields = ('application_no', 'practice_manager',  'application_type', 'payment_amount', 'hospital_name', 'license_category', 'phone', 'email', 'address', 'state', 'city', 'services', 'equipment', 'radiographers', 'radiologists', 'inspection_date', 'inspection_report_deadline', 'inspection_zone', 'inspection_scheduler',)
        widgets = {'application_no': forms.HiddenInput(), 'application_type': forms.HiddenInput(), 'payment_amount': forms.HiddenInput(), 'practice_manager': forms.HiddenInput(), 'hospital_name': forms.HiddenInput(), 'license_category': forms.HiddenInput(), 'phone': forms.HiddenInput(), 'email': forms.HiddenInput(), 'address': forms.HiddenInput(), 'state': forms.HiddenInput(), 'city': forms.HiddenInput(),  'services': forms.HiddenInput(), 'equipment': forms.HiddenInput(), 'radiographers': forms.HiddenInput(), 'radiologists': forms.HiddenInput(),}

         
                                                                                                                                                                            

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
    #license_status = forms.ChoiceField(choices = LICENSE_STATUS, widget=forms.Select(), required=True)

    

    class Meta:
        model = License
        fields = ('application_no', 'practice_manager', 'application_type', 'payment_amount', 'hospital_name', 'license_category', 'address', 'phone', 'email', 'inspection_date', 'issue_date', 'expiry_date', 'license_no', 'license_type')
        widgets = {'application_no': forms.HiddenInput(), 'application_type': forms.HiddenInput(), 'payment_amount': forms.HiddenInput(), 'practice_manager': forms.HiddenInput(), 'hospital_name': forms.HiddenInput(), 'license_category': forms.HiddenInput(), 'phone': forms.HiddenInput(), 'email': forms.HiddenInput(), 'address': forms.HiddenInput(), 'inspection_date': forms.HiddenInput(),}


    
      
       
    def __init__(self, *args, **kwargs):
       super(LicenseModelForm, self).__init__(*args, **kwargs)
       self.fields['issue_date'].label = "Issue Date"
       self.fields['expiry_date'].label = "Expiry Date"
       self.fields['license_no'].label = "License No"
       #self.fields['license_status'].label = "License Status"
    




       
    
      

    
      
       

    




class RecordsModelForm(forms.ModelForm):
    next_visitation_date = forms.DateField(
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

    state = forms.ChoiceField(choices = STATE_CHOICES, widget=forms.Select(), required=True)
    practice_category = forms.ChoiceField(choices = SERVICES, widget=forms.Select(), required=True)
    equipment = forms.MultipleChoiceField(choices = EQUIPMENT, widget=forms.CheckboxSelectMultiple())

    class Meta:
         model = Records
         fields = ('hospital_name', 'practice_category', 'phone', 'email', 'state', 'city', 'address', 'equipment', 'radiographers', 'radiologists', 'inspection_zone', 'visitation_reason', 'visitation_comments', 'next_visitation_date', 'cac_certificate', 'practice_license1', 'practice_license2', 'form_c07',)
         

         widgets = {
         
         'radiographers': forms.Textarea(attrs={'rows':4, 'cols':12}),
         'radiologists': forms.Textarea(attrs={'rows':4, 'cols':12}),
         'visitation_comments': forms.Textarea(attrs={'rows':4, 'cols':12}),
         }


    def __init__(self, *args, **kwargs):
       super(RecordsModelForm, self).__init__(*args, **kwargs)
       self.fields['hospital_name'].label = "Hospital Name"
       self.fields['phone'].label = "Phone No"
       self.fields['email'].label = "Email"
       self.fields['state'].label = "State"
       self.fields['city'].label = "City"
       self.fields['address'].label = "Address"
       self.fields['practice_category'].label = "Practice Category"
       self.fields['equipment'].label = "Available Equipment"
       self.fields['radiographers'].label = "Radiographers"
       self.fields['radiologists'].label = "Radiologists"
       self.fields['visitation_reason'].label = "Reason for Visit"
       self.fields['inspection_zone'].label = "Inspecting Zonal Office"
       self.fields['visitation_comments'].label = "Comments/Observations"
       self.fields['next_visitation_date'].label = "Next Visitation Date"
       self.fields['cac_certificate'].label = "CAC Certificate"
       self.fields['practice_license1'].label = "Radiographer Practice License"
       self.fields['practice_license2'].label = "Radiographer Practice License"
       self.fields['form_c07'].label = "Form C07"


    
    
    
      
     



        



    


		


