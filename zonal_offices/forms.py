from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Inspection
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field




class InspectionModelForm(forms.ModelForm):

    
    
    

    class Meta:
        model = Inspection
        fields = ('application_no', 'practice_manager', 'hospital_name', 'license_category', 'address', 'phone', 'email', 'radiographers', 'radiologists', 'equipment', 'inspection_schedule_date', 'inspection_report_deadline', 'shielding_score', 'equipment_layout_score', 'radiographer_no_score', 'radiologist_certification_score', 'radiographer_license_score', 'personnel_monitoring_score', 'room_adequacy_score', 'water_supply_score', 'equipment_certification_score', 'accessories_score', 'warning_light_score', 'C07_form_compliance_score', 'functional_equipment_score', 'equipment_installation_score', 'darkroom_score', 'public_safety_score', 'inspection_total', 'inspection_comments', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6',)
            
        
        widgets = {
        'practice_manager': forms.HiddenInput(),
        'license_category': forms.HiddenInput(),
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

      


   



        



    


		


