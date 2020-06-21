from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Inspection
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from hospitals.choices import SCORE




class InspectionModelForm(forms.ModelForm):

    
    
    

    class Meta:
        model = Inspection
        fields = ('application_no', 'practice_manager', 'hospital_name', 'license_category',  'address', 'phone', 'email', 'radiographers', 'equipment', 'inspection_schedule_date', 'inspection_report_deadline', 'shielding', 'equipment_layout', 'radiographer_no', 'radiologist_certification', 'radiographer_license', 'personnel_monitoring', 'room_adequacy', 'water_supply', 'equipment_certification', 'accessories', 'warning_light', 'C07_form_compliance', 'functional_equipment', 'equipment_installation', 'darkroom', 'public_safety', 'inspection_total', 'inspection_comments', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6',)
            
        
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
       self.fields['shielding'].label = "Shielding"
       self.fields['shielding'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['equipment_layout'].label = "Equipment Layout"
       self.fields['equipment_layout'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['radiographer_no'].label = "Radiographes' Sufficiency"
       self.fields['radiographer_no'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['radiologist_certification'].label = "Radiologist Certification"
       self.fields['radiologist_certification'].widget.attrs['placeholder'] = "(Max Score = 7)"
       self.fields['radiographer_license'].label = "Radiographers Current License"
       self.fields['radiographer_license'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['personnel_monitoring'].label = "Personnel Monitoring"
       self.fields['personnel_monitoring'].widget.attrs['placeholder'] = "(Max Score = 20)"
       self.fields['room_adequacy'].label = "Adequacy of Room"
       self.fields['room_adequacy'].widget.attrs['placeholder'] = "(Max Score = 7)"
       self.fields['water_supply'].label = "Water Supply"
       self.fields['water_supply'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['equipment_certification'].label = "Equipment Certification"
       self.fields['equipment_certification'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['accessories'].label = "Adequacy of Accessories"
       self.fields['accessories'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['warning_light'].label = "Warning Light"
       self.fields['warning_light'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['C07_form_compliance'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['functional_equipment'].label = "No of Functional Equipment"
       self.fields['functional_equipment'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation'].label = "Equipment Installation"
       self.fields['equipment_installation'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['darkroom'].label = "Darkroom/Digital Room"
       self.fields['darkroom'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['public_safety'].label = "Public Safety/Cleanliness"
       self.fields['public_safety'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['inspection_total'].label = "Total Score"
       self.fields['inspection_comments'].label = "Enter Observations and Comments"

      


   



        



    


		


