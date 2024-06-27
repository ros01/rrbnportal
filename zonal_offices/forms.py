from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from hospitals.models import Inspection, Records, Appraisal, Ultrasound, Mri, Xray, Ctscan, Flouroscopy, Radiotherapy, Nuclearmedicine, Mamography, Dentalxray, Echocardiography, Angiography, Carm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.utils import timezone
from tempus_dominus.widgets import DatePicker
from hospitals.choices import INSPECTION_ZONE, LICENSE_STATUS, STATE_CHOICES, SERVICES, EQUIPMENT
from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.mixins import PassRequestMixin, PopRequestMixin, CreateUpdateAjaxMixin






class InspectionModelForm(forms.ModelForm):

    class Meta:
        model = Inspection
        fields = ('application_no', 'hospital_name', 'hospital', 'payment', 'schedule', 'inspection_comments', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6',)
            
        
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'hospital': forms.HiddenInput(),
        'payment': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
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
       #self.fields['inspection_total'].label = "Total Score"
       self.fields['inspection_comments'].label = "Enter Observations and Comments"


class UltrasoundModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Ultrasound
        fields = ('application_no', 'hospital_name', 'schedule', 'room_design_score', 'radiographers_no_score', 'radiographer_license_score', 'ultrasound_qualification_score', 'water_supply_score', 'accessories_adequacy_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'support_staff_score', 'ultrasound_total' )
            
        
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),  
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'ultrasound_qualification_score': forms.NumberInput(attrs={'min':0,'max':20,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':20,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'support_staff_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}), 
        }

    def __init__(self, *args, **kwargs):                                  
       super(UltrasoundModelForm, self).__init__(*args, **kwargs)

       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['room_design_score'].label = "Room Design"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiographers_no_score'].label = "No of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['ultrasound_qualification_score'].label = "Qualification in Ultrasonography"
       self.fields['ultrasound_qualification_score'].widget.attrs['placeholder'] = "(Max Score = 20)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation"
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 20)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['support_staff_score'].label = "Support Staff (Chaperon)"
       self.fields['support_staff_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['ultrasound_total'].label = "Total Score"

    def save(self):

      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance



class NuclearMedicineModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):                     

    class Meta:
        model = Nuclearmedicine
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'nuclear_medicine_physicians_no_score', 'other_staff_no_score', 'nuclear_medicine_certification_score', 'radiographer_license_score', 'prmd_prpe_score', 'water_supply_score', 'equipment_certification_score', 'radionuclide_accessories_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'radionuclide_storage_unit_score', 'offices_adequacy_score', 'quality_control_score', 'rso_score', 'radiation_safety_program_score', 'labelling_score', 'performance_survey_score', 'radioactive_materials_security_score', 'toilets_cleanliness_score', 'waiting_room_score', 'nuclear_medicine_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),

        'shielding_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'nuclear_medicine_physicians_no_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}), 
        'other_staff_no_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}), 
        'nuclear_medicine_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'radionuclide_storage_unit_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'radionuclide_accessories_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'quality_control_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'rso_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'radiation_safety_program_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'labelling_score': forms.NumberInput(attrs={'min':0,'max':1,'type': 'number'}),
        'performance_survey_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'radioactive_materials_security_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
           
        }

    def __init__(self, *args, **kwargs):
       super(NuclearMedicineModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['nuclear_medicine_physicians_no_score'].label = "Nuclear Medicine Physicians"
       self.fields['nuclear_medicine_physicians_no_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['other_staff_no_score'].label = "No of Other Staff"
       self.fields['other_staff_no_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['nuclear_medicine_certification_score'].label = "Nuclear Medicine Certification"
       self.fields['nuclear_medicine_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['radionuclide_storage_unit_score'].label = "Radionuclide Storage Unit "
       self.fields['radionuclide_storage_unit_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['radionuclide_accessories_score'].label = "Radionuclide Accessories "
       self.fields['radionuclide_accessories_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['quality_control_score'].label = "Quality Control"
       self.fields['quality_control_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['rso_score'].label = "Radiation Safety Officer"
       self.fields['rso_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiation_safety_program_score'].label = "Radiation Safety Program"
       self.fields['radiation_safety_program_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['labelling_score'].label = "Radiopharmceuticals Labelling"
       self.fields['labelling_score'].widget.attrs['placeholder'] = "(Max Score = 1)"
       self.fields['performance_survey_score'].label = "Performance Survey Plan"
       self.fields['performance_survey_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radioactive_materials_security_score'].label = "Security of Radioactive Materials"
       self.fields['radioactive_materials_security_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['nuclear_medicine_total'].label = "Total Score"
    
    def save(self):

      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance


class RadiotherapyModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Radiotherapy
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'other_staff_score', 'radiotherapy_certification_score', 'radiographer_license_score', 'prmd_prpe_score', 'rso_score', 'water_supply_score', 'equipment_certification_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'radiotherapy_accessories_score', 'mould_room_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'radiotherapy_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}), 
        'other_staff_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}), 
        'radiotherapy_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'rso_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'radiotherapy_accessories_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'mould_room_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),    
        }


    

    def __init__(self, *args, **kwargs):
       super(RadiotherapyModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['other_staff_score'].label = "No. of Other Staff"
       self.fields['other_staff_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['radiotherapy_certification_score'].label = "Radiotherapy Certification"
       self.fields['radiotherapy_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['rso_score'].label = "Radiation Safety Officer"
       self.fields['rso_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['warning_lights_score'].label = "Warning Lights & Synergies"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['radiotherapy_accessories_score'].label = "Radiotherapy Accessories"
       self.fields['radiotherapy_accessories_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['mould_room_score'].label = "Adequacy of Mould Room"
       self.fields['mould_room_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiotherapy_total'].label = "Total Score"


    def save(self):
      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)
      return instance


class XrayModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Xray 
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'prmd_prpe_score', 'rso_rsa_score', 'water_supply_score', 'equipment_installation_location_score', 'equipment_certification_score', 'accessories_adequacy_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'xray_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),  
        'rso_rsa_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),    
        } 

    def __init__(self, *args, **kwargs):
       super(XrayModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['rso_rsa_score'].label = "Radiation Safety Officer"
       self.fields['rso_rsa_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['xray_total'].label = "Total Score"
      
    def save(self):

      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance


class FlouroscopyModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Flouroscopy
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'prmd_prpe_score', 'rso_rsa_score', 'water_supply_score', 'equipment_installation_location_score', 'equipment_certification_score', 'accessories_adequacy_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'flouroscopy_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'rso_rsa_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),    
        }

    def __init__(self, *args, **kwargs):
       super(FlouroscopyModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['rso_rsa_score'].label = "Radiation Safety Officer"
       self.fields['rso_rsa_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['flouroscopy_total'].label = "Total Score"

    def save(self):
      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance


class CtscanModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Ctscan
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'prmd_prpe_score', 'rso_rsa_score', 'water_supply_score', 'equipment_installation_location_score', 'equipment_certification_score', 'accessories_adequacy_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'ctscan_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':14,'type': 'number'}),
        'rso_rsa_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),    
        }

    def __init__(self, *args, **kwargs):
       super(CtscanModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 14)"
       self.fields['rso_rsa_score'].label = "Radiation Safety Officer"
       self.fields['rso_rsa_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['toilets_cleanliness_score'].label = "Toilets & Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['ctscan_total'].label = "Total Score"

    def save(self):

      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance

class MriModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Mri
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'mri_certification_score', 'metal_screening_device_score', 'screening_questionnaire_score', 'water_supply_score', 'accessories_adequacy_score', 'warning_signs_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'technical_room_adequacy_score', 'mri_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'mri_certification_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'metal_screening_device_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'screening_questionnaire_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':7,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}), 
        'technical_room_adequacy_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),    
        }


    def __init__(self, *args, **kwargs):
       super(MriModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding/Faraday Cage"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['mri_certification_score'].label = "PG Certification in MRI"
       self.fields['mri_certification_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['metal_screening_device_score'].label = "Metal Screening Device"
       self.fields['metal_screening_device_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['screening_questionnaire_score'].label = "Screening Questionnaire"
       self.fields['screening_questionnaire_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 7)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['technical_room_adequacy_score'].label = "Adequacy of Technical Room"
       self.fields['technical_room_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['mri_total'].label = "Total Score"

    def save(self):

      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance


class MamographyModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Mamography
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'mammography_certification_score', 'prmd_prpe_score', 'rso_rsa_score', 'water_supply_score', 'equipment_certification_score', 'accessories_adequacy_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'mamography_total')
          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'mammography_certification_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'rso_rsa_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':4, 'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),    
        }

    def __init__(self, *args, **kwargs):
       super(MamographyModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['mammography_certification_score'].label = "Mammography Certification"
       self.fields['mammography_certification_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['rso_rsa_score'].label = "Radiation Safety Officer"
       self.fields['rso_rsa_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['mamography_total'].label = "Total Score"

    def save(self):

      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance

class DentalXrayModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Dentalxray
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'prmd_prpe_score', 'water_supply_score', 'equipment_certification_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'dentalxray_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':1,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}), 
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),    
        }

    def __init__(self, *args, **kwargs):
       super(DentalXrayModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 1)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['dentalxray_total'].label = "Total Score"

    def save(self):

      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance

class EchocardiographyModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Echocardiography
        fields = ('application_no', 'hospital_name', 'schedule', 'room_design_score', 'radiographers_no_score', 'radiographer_license_score', 'echocardiography_certification_score', 'water_supply_score', 'accessories_adequacy_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'support_staff_score', 'echocardiography_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
       
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'echocardiography_certification_score': forms.NumberInput(attrs={'min':0,'max':20,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':20,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}), 
        'support_staff_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),     
        }  

    def __init__(self, *args, **kwargs):
       super(EchocardiographyModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['echocardiography_certification_score'].label = "Echocardiography Certification"
       self.fields['echocardiography_certification_score'].widget.attrs['placeholder'] = "(Max Score = 20"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 20)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['support_staff_score'].label = "Support Staff/Chaperon"
       self.fields['support_staff_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['echocardiography_total'].label = "Total Score"

    def save(self):
      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

      return instance

class AngiographyModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Angiography
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'angiography_certification_score', 'prmd_prpe_score', 'rso_rsa_score', 'water_supply_score', 'equipment_certification_score', 'accessories_adequacy_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'angiography_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'angiography_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'rso_rsa_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),    
        }

    def __init__(self, *args, **kwargs):
       super(AngiographyModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['angiography_certification_score'].label = "Angiography Certification"
       self.fields['angiography_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['rso_rsa_score'].label = "Radiation Safety Officer"
       self.fields['rso_rsa_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['angiography_total'].label = "Total Score"

    def save(self):
      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)
      return instance


class CarmModelForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):

    class Meta:
        model = Carm
        fields = ('application_no', 'hospital_name', 'schedule', 'shielding_score', 'room_design_score', 'radiographers_no_score', 'radiologists_no_score', 'radiographer_license_score', 'prmd_prpe_score', 'water_supply_score', 'equipment_certification_score', 'accessories_adequacy_score', 'warning_lights_score', 'warning_signs_score', 'C07_form_compliance_score', 'equipment_installation_location_score', 'processing_unit_score', 'toilets_cleanliness_score', 'waiting_room_score', 'offices_adequacy_score', 'carm_total')

          
        widgets = {
        'hospital_name': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        
        'shielding_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'radiographers_no_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}), 
        'radiologists_no_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}), 
        'radiographer_license_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'prmd_prpe_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}), 
        'water_supply_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'equipment_certification_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'accessories_adequacy_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'warning_lights_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'warning_signs_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'C07_form_compliance_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'equipment_installation_location_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'toilets_cleanliness_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'offices_adequacy_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),    
        }

    def __init__(self, *args, **kwargs):
       super(CarmModelForm, self).__init__(*args, **kwargs)
       
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
       self.fields['schedule'].label = ""
       self.fields['hospital_name'].label = ""
       self.fields['shielding_score'].label = "Shielding"
       self.fields['shielding_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['room_design_score'].label = "Room Design & Layout"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['radiographers_no_score'].label = "No. of Radiographers"
       self.fields['radiographers_no_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['radiologists_no_score'].label = "No. of Radiologists"
       self.fields['radiologists_no_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['radiographer_license_score'].label = "Radiographers Current License"
       self.fields['radiographer_license_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['prmd_prpe_score'].label = "PRMD & PRPE"
       self.fields['prmd_prpe_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['water_supply_score'].label = "Water Supply"
       self.fields['water_supply_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['equipment_certification_score'].label = "Equipment Certification"
       self.fields['equipment_certification_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['accessories_adequacy_score'].label = "Adequacy of Accessories"
       self.fields['accessories_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['warning_lights_score'].label = "Warning Lights"
       self.fields['warning_lights_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['warning_signs_score'].label = "Warning Signs"
       self.fields['warning_signs_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['C07_form_compliance_score'].label = "Compliance to Form C07"
       self.fields['C07_form_compliance_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['equipment_installation_location_score'].label = "Equipment Installation "
       self.fields['equipment_installation_location_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['processing_unit_score'].label = "Adequacy of Processing Unit"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['toilets_cleanliness_score'].label = "Toilets and Cleanliness"
       self.fields['toilets_cleanliness_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['waiting_room_score'].label = "Adequacy of Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['offices_adequacy_score'].label = "Adequacy of Offices"
       self.fields['offices_adequacy_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['carm_total'].label = "Total Score"

    def save(self):
      if not self.request.is_ajax():
          instance = super(CreateUpdateAjaxMixin, self).save(commit=True)
          instance.save()
      else:
          instance = super(CreateUpdateAjaxMixin, self).save(commit=False)
      return instance



class AccreditationModelForm(forms.ModelForm):

    class Meta:
        model = Appraisal
        fields = ('application_no', 'hospital_name', 'hospital', 'payment', 'schedule', 'radiographers_score', 'radiologists_score', 'support_staff_score', 'offices_score', 'library_score', 'call_room_score', 'waiting_room_score', 'toilets_score', 'room_design_score', 'static_xray_score', 'mobile_xray_score', 'ct_score', 'mri_score', 'fluoroscopy_score', 'nuclear_medicine_score', 'radiation_therapy_score', 'ultrasound_score', 'mammography_score', 'dental_equipment_score', 'carm_score', 'processing_unit_score', 'diagnostic_room_score', 'personnel_score',  'cpds_score', 'departmental_seminars_score', 'licence_status_score', 'appraisal_total',  'appraisal_comments', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6',)      
        
        widgets = {
        
        'hospital_name': forms.HiddenInput(),
        'hospital': forms.HiddenInput(),
        'payment': forms.HiddenInput(),
        'schedule': forms.HiddenInput(),
        'application_no': forms.TextInput(attrs={'readonly': True}),

        #'hospital_name': forms.TextInput(attrs={'readonly': True}),
        #'application_no': forms.TextInput(attrs={'readonly': True}),
        'appraisal_comments': forms.Textarea(attrs={'rows':6, 'cols':12}),
        'shielding_score': forms.NumberInput(attrs={'min':1,'max':10,'type': 'number'}),
        'radiographers_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'radiologists_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}), 
        'support_staff_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}), 
        'offices_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'library_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'call_room_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'waiting_room_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'toilets_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'room_design_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'static_xray_score': forms.NumberInput(attrs={'min':0,'max':15,'type': 'number'}),
        'mobile_xray_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'ct_score': forms.NumberInput(attrs={'min':0,'max':5,'type': 'number'}),
        'mri_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'fluoroscopy_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'nuclear_medicine_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'radiation_therapy_score': forms.NumberInput(attrs={'min':0,'max':1,'type': 'number'}), 
        'ultrasound_score': forms.NumberInput(attrs={'min':0,'max':10,'type': 'number'}),
        'mammography_score': forms.NumberInput(attrs={'min':0,'max':3,'type': 'number'}),
        'dental_equipment_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'carm_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'processing_unit_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
        'diagnostic_room_score': forms.NumberInput(attrs={'min':0,'max':6,'type': 'number'}),
        'personnel_score': forms.NumberInput(attrs={'min':0,'max':8,'type': 'number'}),
        'cpds_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'departmental_seminars_score': forms.NumberInput(attrs={'min':0,'max':2,'type': 'number'}),
        'licence_status_score': forms.NumberInput(attrs={'min':0,'max':4,'type': 'number'}),
         
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
       self.fields['support_staff_score'].label = "Support Score"
       self.fields['support_staff_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['offices_score'].label = "Offices Score"
       self.fields['offices_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['library_score'].label = "Library Score"
       self.fields['library_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['call_room_score'].label = "Call Room"
       self.fields['call_room_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['waiting_room_score'].label = "Waiting Room"
       self.fields['waiting_room_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['toilets_score'].label = "Toilets Score"
       self.fields['toilets_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['static_xray_score'].label = "Static X-Ray Score"
       self.fields['static_xray_score'].widget.attrs['placeholder'] = "(Max Score = 15)"
       self.fields['mobile_xray_score'].label = "Mobile X-Ray Score"
       self.fields['mobile_xray_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['ct_score'].label = "CT Scan Score"
       self.fields['ct_score'].widget.attrs['placeholder'] = "(Max Score = 5)"
       self.fields['mri_score'].label = "MRI Score"
       self.fields['mri_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['fluoroscopy_score'].label = "Flouroscopy Score"
       self.fields['fluoroscopy_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['nuclear_medicine_score'].label = "Nuclear Medicine"
       self.fields['nuclear_medicine_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['radiation_therapy_score'].label = "Radiation Therapy Score"
       self.fields['radiation_therapy_score'].widget.attrs['placeholder'] = "(Max Score = 1)"
       self.fields['ultrasound_score'].label = "Ultrasound Score"
       self.fields['ultrasound_score'].widget.attrs['placeholder'] = "(Max Score = 10)"
       self.fields['mammography_score'].label = "Mammography Score"
       self.fields['mammography_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['dental_equipment_score'].label = "Dental Equipment Score"
       self.fields['dental_equipment_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['carm_score'].label = "C-Arm Score"
       self.fields['carm_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['processing_unit_score'].label = "Processing Unit Score"
       self.fields['processing_unit_score'].widget.attrs['placeholder'] = "(Max Score = 4)"
       self.fields['diagnostic_room_score'].label = "Diagnostic Room Score"
       self.fields['diagnostic_room_score'].widget.attrs['placeholder'] = "(Max Score = 6)"
       self.fields['personnel_score'].label = "Personnel Monitoring Score"
       self.fields['personnel_score'].widget.attrs['placeholder'] = "(Max Score = 8)"
       self.fields['cpds_score'].label = "CPDs Score"
       self.fields['cpds_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['departmental_seminars_score'].label = "Departmental Seminars Score"
       self.fields['departmental_seminars_score'].widget.attrs['placeholder'] = "(Max Score = 2)"
       self.fields['room_design_score'].label = "Room Design Score"
       self.fields['room_design_score'].widget.attrs['placeholder'] = "(Max Score = 3)"
       self.fields['licence_status_score'].label = "Current License Score"
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



        


    


		


