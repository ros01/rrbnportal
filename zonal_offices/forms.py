from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Inspection
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from hospitals.choices import SCORE




class InspectionModelForm(forms.ModelForm):

    shielding = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    equipment_layout = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    radiographer_adequacy = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    radiographer_license = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    personnel_monitoring = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    room_size = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    water_supply = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    C07_form_compliance = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    darkroom = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    public_safety = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    functional_equipment = forms.ChoiceField(choices = SCORE, widget=forms.Select(), required=True)
    
    

    class Meta:
        model = Inspection
        fields = ('application_no', 'practice_manager', 'hospital_name', 'license_category',  'address', 'phone', 'email', 'radiographers', 'inspection_schedule_date', 'inspection_report_deadline', 'inspection_scores', 'shielding', 'equipment', 'equipment_layout', 'functional_equipment', 'radiographer_adequacy', 'radiographer_license', 'personnel_monitoring', 'room_size', 'water_supply', 'C07_form_compliance', 'darkroom', 'public_safety', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6',)
            
        
        widgets = {
        'practice_manager': forms.HiddenInput(),
        'license_category': forms.HiddenInput(),
        'inspection_report_deadline': forms.HiddenInput(),
        'inspection_schedule_date': forms.HiddenInput(),
        'hospital_name': forms.TextInput(attrs={'readonly': True}),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        
       
        }

    def __init__(self, *args, **kwargs):
       super(InspectionModelForm, self).__init__(*args, **kwargs)
       #self.fields['inspection_zone'].label = False
       #self.fields['inspection_date'].label = "Inspection Date"
       #self.fields['inspection_report_deadline'].label = "Inspection Report Deadline"




        



    


		


