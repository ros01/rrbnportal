from django import forms
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import *
from accounts.models import Hospital
from .models import *
from tempus_dominus.widgets import DatePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from hospitals.choices import INSPECTION_ZONE, LICENSE_STATUS, STATE_CHOICES, SERVICES, EQUIPMENT
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
# from bootstrap_datepicker_plus.widgets import DatePickerInput


class DocumentForm(forms.ModelForm):
    class Meta:
        model = DocumentUpload
        fields = ('description', 'document', )
        

class InternshipListForm(forms.ModelForm):
    class Meta:
        model = InternshipList
        fields = ('file', )



class ScheduleModelForm(forms.ModelForm):
    inspectors = forms.ModelMultipleChoiceField(
        queryset=Inspector.objects.none(),  # Dynamically populated
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Inspectors"
    )

    inspection_date = forms.DateField(
        widget=DatePicker(
            options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                # 'maxDate': '2025-12-31',
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
                # 'maxDate': '2025-12-31',
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
                }
                )
        )

    class Meta:
        model = Schedule
        fields = [
            'application_no', 
            'hospital', 
            'hospital_name', 
            'payment', 
            'inspection_scheduler', 
            'inspection_schedule_date', 
            'inspection_date', 
            'inspection_report_deadline', 
            'inspection_zone',
            'inspector1_name',
            'inspector1_phone',
            'inspector2_name',
            'inspector2_phone',
            'inspector3_name',
            'inspector3_phone',
            'inspector4_name',
            'inspector4_phone',
            'inspector5_name',
            'inspector5_phone',
            'inspector6_name',
            'inspector6_phone',
            # 'inspectors',  # Assuming this field is a many-to-many or foreign key for inspectors
        ]

        widgets = {
         'application_no': forms.HiddenInput(),
         'hospital_name': forms.HiddenInput(),
         'hospital': forms.HiddenInput(),
         'payment': forms.HiddenInput(),
         } 

    def __init__(self, *args, **kwargs):
       super(ScheduleModelForm, self).__init__(*args, **kwargs)
       self.fields['inspection_zone'].label = False
       self.fields['inspection_date'].label = "Inspection Date"
       self.fields['inspector1_name'].label = "Inspector 1 Name"
       self.fields['inspector1_phone'].label = "Inspector 1 Phone"
       self.fields['inspector2_name'].label = "Inspector 2 Name"
       self.fields['inspector2_phone'].label = "Inspector 2 Phone"
       self.fields['inspector3_name'].label = "Inspector 3 Name"
       self.fields['inspector3_phone'].label = "Inspector 3 Phone"
       self.fields['inspector4_name'].label = "Inspector 4 Name"
       self.fields['inspector4_phone'].label = "Inspector 4 Phone"
       self.fields['inspector5_name'].label = "Inspector 5 Name"
       self.fields['inspector5_phone'].label = "Inspector 5 Phone"
       self.fields['inspector6_name'].label = "Inspector 6 Name"
       self.fields['inspector6_phone'].label = "Inspector 6 Phone"
       self.fields['inspection_report_deadline'].label = "Inspection Report Deadline"


    def clean(self):
        cleaned_data = super().clean()
        inspector1_name = cleaned_data.get('inspector1_name')
        inspector1_phone = cleaned_data.get('inspector1_phone')

        if not inspector1_name or not inspector1_phone:
            raise forms.ValidationError("Inspector 1 details are required.")
        return cleaned_data


# 

    # def __init__(self, *args, **kwargs):
    #     zone = kwargs.pop('zone', None)  # Pass the zone dynamically
    #     super().__init__(*args, **kwargs)
    #     if zone:
            # Filter inspectors based on the selected zone
        #     self.fields['inspectors'].queryset = Inspector.objects.filter(zone=zone)
        # else:
        #     self.fields['inspectors'].queryset = Inspector.objects.all()


class ScheduleModelForm0(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            'application_no', 
            'hospital', 
            'hospital_name', 
            'payment', 
            'inspection_scheduler', 
            'inspection_schedule_date', 
            'inspection_date', 
            'inspection_report_deadline', 
            'inspection_zone',
            # 'inspectors',  # Assuming this field is a many-to-many or foreign key for inspectors
        ]
        widgets = {
            'inspection_schedule_date': forms.DateInput(attrs={'type': 'date'}),
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'inspection_report_deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Pass additional arguments if needed
        inspectors_queryset = kwargs.pop('inspectors_queryset', None)
        super(ScheduleModelForm, self).__init__(*args, **kwargs)

        # Add a placeholder for each field if needed
        self.fields['application_no'].widget.attrs.update({'placeholder': 'Application Number'})
        self.fields['inspection_zone'].widget.attrs.update({'hx-get': '/get-inspectors/', 'hx-target': '#inspectors-dropdown', 'hx-trigger': 'change'})

        # Dynamically filter inspectors by zone if provided
        # if inspectors_queryset is not None:
        #     self.fields['inspectors'].queryset = inspectors_queryset

        # Optional: Add labels or help texts
        # self.fields['inspectors'].label = "Select Inspectors"
        # self.fields['inspectors'].help_text = "Inspectors available for the selected zone."

        # Customize any field as required
        # self.fields['inspectors'].required = True


class ScheduleModelForm1(forms.ModelForm):
    # inspectors = forms.ModelChoiceField(
    #     queryset=Inspector.objects.none(),  # Initially empty
    #     required=True,
    #     label="Inspector",
    # )

    inspectors = forms.ModelMultipleChoiceField(
        queryset=Inspector.objects.filter(is_approved=True),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Approved Inspectors"
    )



    inspection_date = forms.DateField(
    	widget=DatePicker(
    		options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                # 'maxDate': '2025-12-31',
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
                # 'maxDate': '2025-12-31',
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
        fields = ('application_no', 'hospital_name', 'hospital', 'payment',  'inspection_date', 'inspection_report_deadline', 'inspection_zone', 'inspection_scheduler')
       
        widgets = {
         'application_no': forms.HiddenInput(),
         'hospital_name': forms.HiddenInput(),
         'hospital': forms.HiddenInput(),
         'payment': forms.HiddenInput(),
         } 
             
    # def __init__(self, *args, **kwargs):
    #     selected_zone = kwargs.pop('selected_zone', None)
    #     super().__init__(*args, **kwargs)
    #     if selected_zone:
    #         self.fields['inspectors'].queryset = Inspector.objects.filter(zone=selected_zone)
    #     else:
    #         self.fields['inspectors'].queryset = Inspector.objects.none()                                                                                                                   

    def __init__(self, *args, **kwargs):
       super(ScheduleModelForm, self).__init__(*args, **kwargs)
       self.fields['inspection_zone'].label = False
       self.fields['inspection_date'].label = "Inspection Date"
       self.fields['inspection_report_deadline'].label = "Inspection Report Deadline"

       # selected_zone = kwargs.pop('selected_zone', None)
       # super().__init__(*args, **kwargs)
       # if selected_zone:
       #      self.fields['inspectors'].queryset = Inspector.objects.filter(zone=selected_zone)
       # else:
       #      self.fields['inspectors'].queryset = Inspector.objects.none() 



class LicenseModelForm(forms.ModelForm):
    issue_date = forms.DateField(
        widget=DatePicker(
            options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                # 'maxDate': '2025-12-31',
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
                # 'maxDate': '2025-12-31',
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
        fields = ('application_no', 'hospital_name', 'hospital', 'payment', 'schedule', 'inspection', 'issue_date', 'expiry_date', 'license_class', 'license_no')
        widgets = {
          'application_no': forms.HiddenInput(),
          'hospital_name': forms.HiddenInput(),
          'hospital': forms.HiddenInput(),
          'payment': forms.HiddenInput(),
          'schedule': forms.HiddenInput(),
          'inspection': forms.HiddenInput(),
        } 
      
       
    def __init__(self, *args, **kwargs):
       super(LicenseModelForm, self).__init__(*args, **kwargs)
       self.fields['issue_date'].label = "Issue Date"
       self.fields['expiry_date'].label = "Expiry Date"
       self.fields['license_no'].label = "Permit No"
       #self.fields['license_status'].label = "License Status"
    

class PermitRenewalModelForm(forms.ModelForm):
    issue_date = forms.DateField(
        widget=DatePicker(
            options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                # 'maxDate': '2025-12-31',
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
                # 'maxDate': '2025-12-31',
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
        fields = ('application_no', 'hospital_name', 'hospital', 'payment', 'issue_date', 'expiry_date', 'license_class', 'license_no')
        widgets = {
          'application_no': forms.HiddenInput(),
          'hospital_name': forms.HiddenInput(),
          'hospital': forms.HiddenInput(),
          'payment': forms.HiddenInput(),
          #'schedule': forms.HiddenInput(),
          #'inspection': forms.HiddenInput(),
        } 
      
       
    def __init__(self, *args, **kwargs):
       super(PermitRenewalModelForm, self).__init__(*args, **kwargs)
       self.fields['issue_date'].label = "Issue Date"
       self.fields['expiry_date'].label = "Expiry Date"
       self.fields['license_no'].label = "Permit No"
       self.fields['license_class'].label = "Class of Permit"
       #self.fields['license_status'].label = "License Status"


class AccreditationModelForm(forms.ModelForm):
    issue_date = forms.DateField(
        widget=DatePicker(
            options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                # 'maxDate': '2025-12-31',
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
                # 'maxDate': '2025-12-31',
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
        fields = ('application_no', 'hospital_name', 'hospital', 'payment', 'schedule', 'appraisal', 'issue_date', 'expiry_date', 'license_class', 'license_no')
        widgets = {
          'application_no': forms.HiddenInput(),
          'hospital_name': forms.HiddenInput(),
          'hospital': forms.HiddenInput(),
          'payment': forms.HiddenInput(),
          'schedule': forms.HiddenInput(),
          'appraisal': forms.HiddenInput(),
        } 
      
       
    def __init__(self, *args, **kwargs):
       super(AccreditationModelForm, self).__init__(*args, **kwargs)
       self.fields['issue_date'].label = "Issue Date"
       self.fields['expiry_date'].label = "Expiry Date"
       self.fields['license_no'].label = "Certificate No"
       #self.fields['license_status'].label = "License Status"

class HospitalProfileModelForm(forms.ModelForm):
      
    class Meta:
         model = Hospital
         fields = ('hospital_name', 'hospital_admin', 'phone_no', 'rc_number', 'state', 'city', 'type', 'contact_address')
         

         widgets = {
            'contact_address': forms.Textarea(attrs={'rows':2, 'cols':3}),
            'hospital_admin': forms.HiddenInput(),
            'type': forms.HiddenInput(),
            # 'dob': DatePickerInput(),
            
         }

    def __init__(self, *args, **kwargs):
       super(HospitalProfileModelForm, self).__init__(*args, **kwargs)
       self.fields['hospital_name'].label = "Hospital Name"
       self.fields['phone_no'].label = "Mobile Telephone Number"
       self.fields['state'].label = "State of Location"
       self.fields['city'].label = "City of Location"
       self.fields['contact_address'].label = "Contact Address"
       self.fields['rc_number'].label = "RC Number"
       self.fields['rc_number'].widget.attrs['placeholder'] = "Leave blank if no RC Number"
      



class RecordsModelForm(forms.ModelForm):
    next_visitation_date = forms.DateField(
        widget=DatePicker(
            options={
                'useCurrent': True,
                'collapse': False,
                'minDate': '2020-06-05',
                # 'maxDate': '2025-12-31',
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


    
    
    
      
     



        



    


		


