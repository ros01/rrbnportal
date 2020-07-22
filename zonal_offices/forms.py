from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Inspection, Records, Appraisal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.utils import timezone
from tempus_dominus.widgets import DatePicker
from hospitals.choices import INSPECTION_ZONE, LICENSE_STATUS, STATE_CHOICES, SERVICES, EQUIPMENT




class InspectionModelForm(forms.ModelForm):

    class Meta:
        model = Inspection
        fields = ('application_no', 'practice_manager','application_type', 'payment_amount', 'hospital_name', 'license_category', 'address', 'phone', 'email', 'radiographers', 'radiologists', 'inspection_zone',  'equipment', 'inspection_schedule_date', 'inspection_report_deadline', 'shielding_score', 'equipment_layout_score', 'radiographer_no_score', 'radiologist_certification_score', 'radiographer_license_score', 'personnel_monitoring_score', 'room_adequacy_score', 'water_supply_score', 'equipment_certification_score', 'accessories_score', 'warning_light_score', 'C07_form_compliance_score', 'functional_equipment_score', 'equipment_installation_score', 'darkroom_score', 'public_safety_score', 'inspection_total', 'inspection_comments', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6',)
            
        
        widgets = {
        'practice_manager': forms.HiddenInput(),
        'license_category': forms.HiddenInput(),
        'application_type': forms.HiddenInput(),
        'payment_amount': forms.HiddenInput(),
        'inspection_report_deadline': forms.HiddenInput(),
        'inspection_schedule_date': forms.HiddenInput(),
        'hospital_name': forms.TextInput(attrs={'readonly': True}),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        'inspection_comments': forms.Textarea(attrs={'rows':6, 'cols':12}),
     
        
       
        }

    def __init__(self, *args, **kwargs):
       super(InspectionModelForm, self).__init__(*args, **kwargs)
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       #self.fields['inspection_zone'].label = False
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['equipment_layout_score'].label = "Equipment Layout"
       self.fields['equipment_layout_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['radiographer_no_score'].label = "Radiographes' Sufficiency"
       self.fields['radiographer_no_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['radiologist_certification_score'].label = "Radiologist Certification"
       self.fields['radiologist_certification_score'].widget.attrs['placeholder'] = "(Max Score = 7)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['personnel_monitoring_score'].label = "Personnel Monitoring"
       self.fields['personnel_monitoring_score'].widget.attrs['placeholder'] = "(Max Score = 20)"
       self.fields['room_adequacy_score'].label = "Adequacy of Room"
       self.fields['room_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 7)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['accessories_score'].label = "Adequacy of Accessories"
       self.fields['accessories_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['warning_light_score'].label = "Warning Light"
       self.fields['warning_light_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['functional_equipment_score'].label = "No of Functional Equipment"
       self.fields['functional_equipment_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_score'].label = "Equipment Installation"
       self.fields['equipment_installation_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['darkroom_score'].label = "Darkroom/Digital Room"
       self.fields['darkroom_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['public_safety_score'].label = "Public Safety/Cleanliness"
       self.fields['public_safety_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['inspection_total'].label = "Total Score"
       self.fields['inspection_comments'].label = "Enter Observations and Comments"


class AccreditationModelForm(forms.ModelForm):

    class Meta:
        model = Appraisal
        fields = ('application_no', 'practice_manager','application_type', 'payment_amount', 'hospital_name', 'license_category', 'address', 'phone', 'email', 'radiographers', 'radiologists', 'inspection_zone',  'equipment', 'inspection_schedule_date', 'inspection_report_deadline', 'radiographers_score', 'radiologists_score', 'darkroom_technicians_score', 'offices_score', 'library_score', 'call_room_score', 'waiting_room_score', 'toilets_score', 'static_xray_score', 'mobile_xray_score', 'ct_score', 'mri_score', 'fluoroscopy_score', 'nuclear_medicine_score', 'radiation_therapy_score', 'ultrasound_score', 'mammography_score', 'dental_equipment_score', 'carm_score', 'processing_room_score', 'diagnostic_room_score', 'personnel_monitoring_score', 'warning_light_score', 'warning_signs_score', 'cpds_score', 'departmental_seminars_score', 'licence_status_score', 'appraisal_total',  'appraisal_comments', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6',)
            
        
        widgets = {
        'practice_manager': forms.HiddenInput(),
        'license_category': forms.HiddenInput(),
        'application_type': forms.HiddenInput(),
        'payment_amount': forms.HiddenInput(),
        'inspection_report_deadline': forms.HiddenInput(),
        'inspection_schedule_date': forms.HiddenInput(),
        'hospital_name': forms.TextInput(attrs={'readonly': True}),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        'appraisal_comments': forms.Textarea(attrs={'rows':6, 'cols':12}),
     
        
       
        }

    def __init__(self, *args, **kwargs):
       super(AccreditationModelForm, self).__init__(*args, **kwargs)
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       #self.fields['inspection_zone'].label = False
       self.fields['radiographers_score'].label = "Radiographers Score"
       self.fields['radiographers_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['radiologists_score'].label = "Radiologists Score"
       self.fields['radiologists_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['darkroom_technicians_score'].label = "Darkroom Technician Score"
       self.fields['darkroom_technicians_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['offices_score'].label = "Offices Score"
       self.fields['offices_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['library_score'].label = "Library Score"
       self.fields['library_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['call_room_score'].label = "Call Room"
       self.fields['call_room_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['waiting_room_score'].label = "Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['toilets_score'].label = "Toilets Score"
       self.fields['toilets_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['static_xray_score'].label = "Static X-Ray Score"
       self.fields['static_xray_score'].widget.attrs['placeholder'] = "(Max Score = 20)"
       self.fields['mobile_xray_score'].label = "Mobile X-Ray Score"
       self.fields['mobile_xray_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['ct_score'].label = "CT Score"
       self.fields['ct_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['mri_score'].label = "MRI"
       self.fields['mri_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['fluoroscopy_score'].label = "Flouroscopy Score"
       self.fields['fluoroscopy_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['nuclear_medicine_score'].label = "Nuclear Medicine"
       self.fields['nuclear_medicine_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiation_therapy_score'].label = "Radiation Therapy Score"
       self.fields['radiation_therapy_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['ultrasound_score'].label = "Ultrasound Score"
       self.fields['ultrasound_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['mammography_score'].label = "Mammography Score"
       self.fields['mammography_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['dental_equipment_score'].label = "Dental Equipment Score"
       self.fields['dental_equipment_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['carm_score'].label = "C-Arm Score"
       self.fields['carm_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['processing_room_score'].label = "Processing Room Score"
       self.fields['processing_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['diagnostic_room_score'].label = "Diagnostic Room Score"
       self.fields['diagnostic_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['personnel_monitoring_score'].label = "Personnel Monitoring Score"
       self.fields['personnel_monitoring_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_light_score'].label = "Warning Light Score"
       self.fields['warning_light_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['warning_signs_score'].label = "Warning Signs Score"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['cpds_score'].label = "CPDs Score"
       self.fields['cpds_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['departmental_seminars_score'].label = "Departmental Seminars Score"
       self.fields['departmental_seminars_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['licence_status_score'].label = "License Status Score"
       self.fields['licence_status_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['appraisal_total'].label = "Total Score"
       self.fields['appraisal_comments'].label = "Enter Observations and Comments"

      

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



        



    


		


