from django import forms
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import Document, Payment
from .choices import *
from django.forms.widgets import CheckboxSelectMultiple
from django.forms import MultipleChoiceField
from django.forms.models import ModelMultipleChoiceField
from django.forms import MultipleChoiceField
from django.contrib.auth import get_user_model
from accounts.models import Hospital


User = get_user_model()


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
      


class HospitalProfileUpdateModelForm(forms.ModelForm):
    type = forms.ChoiceField(choices = APPLICATION_CATEGORY, widget=forms.Select(), required=True)
      
    class Meta:
         model = Hospital
         fields = ('hospital_admin', 'type')
         

         widgets = {
            # 'contact_address': forms.Textarea(attrs={'rows':2, 'cols':3}),
            'hospital_admin': forms.HiddenInput(),
            # 'type': forms.HiddenInput(),
            # 'dob': DatePickerInput(),
            
         }

    def __init__(self, *args, **kwargs):
       super(HospitalProfileUpdateModelForm, self).__init__(*args, **kwargs)
       self.fields['hospital_admin'].label = "Hospital Admin"
       self.fields['type'].label = ""
       # self.fields['phone_no'].label = "Mobile Telephone Number"
       # self.fields['state'].label = "State of Location"
       # self.fields['city'].label = "City of Location"
       # self.fields['contact_address'].label = "Contact Address"
       # self.fields['rc_number'].label = "RC Number"
       # self.fields['rc_number'].widget.attrs['placeholder'] = "Leave blank if no RC Number"


class HospitalDetailModelForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('license_type', 'application_type', 'hospital_name', 'hospital_type', 'facility_address', 'facility_state_of_location', 'equipment', 'radiographer_in_charge', 'radiographer1', 'radiographer2', 'radiographer3', 'radiographer_in_charge_license_no', 'radiographer1_license_no', 'radiographer2_license_no', 'radiographer3_license_no', 'staffname1', 'staffname2', 'staffname3', 'staffname4', 'staffname5', 'staffdesignation1', 'staffdesignation2', 'staffdesignation3', 'staffdesignation4', 'staffdesignation5', 'radiographer_in_charge_passport', 'radiographer_in_charge_nysc', 'radiographer_in_charge_practice_license', 'radiographer1_practice_license', 'radiographer2_practice_license', 'radiographer3_practice_license', 'cac_certificate', 'form_c07')

        widgets = {
            'facility_address': forms.Textarea(attrs={'rows':3, 'cols':5}), 
            #'radiologists': forms.Textarea(attrs={'rows':3, 'cols':5}),
            #'license_type': forms.HiddenInput(),
            'hospital_name': forms.HiddenInput(),   
                                
            }

    def __init__(self, *args, **kwargs):
      
       super(HospitalDetailModelForm, self).__init__(*args, **kwargs)
       for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

       self.fields['application_type'].label = "Application Type"
       self.fields['application_type'].widget.attrs['placeholder'] = "Enter Application Type"
       #self.fields['license_type'].widget.attrs['value'] = self.instance.license_type
       #self.fields['license_type'].widget.attrs['readonly'] = 'readonly'
       self.fields['license_type'].label = "License Type"
       #self.fields['license_type'].label = "License Type"
       #self.fields['license_type'].label_from_instance = lambda obj: "{}".format(obj.license_type)
       
       self.fields['hospital_type'].label = "Hospital Type"
       self.fields['hospital_type'].widget.attrs['placeholder'] = "Enter Hospital Type"
       #self.fields['hospital_name'].label_from_instance = lambda obj: "{}".format(obj.hospital_name)
       #self.fields['hospital_name'].initial = hospital_name.hospital_name
       #self.fields['hospital_name'].widget.attrs['readonly'] = 'readonly'
       #self.fields['hospital_name'].label = "Hospital Name"
       self.fields['facility_address'].label = "Hospital/Centre Address*"
       self.fields['facility_address'].widget.attrs['placeholder'] = "Enter Address of Hospital/Centre"
       self.fields['facility_state_of_location'].label = "State of Location of Hospital/Centre"
       self.fields['facility_state_of_location'].widget.attrs['placeholder'] = "Enter State of Location of Hospital/Centre"
       self.fields['equipment'].label = "Available Equipment"
       self.fields['equipment'].widget = CheckboxSelectMultiple()
       self.fields['radiographer_in_charge'].label = "Radiographer In Charge"
       self.fields['radiographer_in_charge'].widget.attrs['placeholder'] = "Enter Name of R.I.Charge (Required) "
       self.fields['radiographer1'].label = "Radiographer 1"
       self.fields['radiographer1'].widget.attrs['placeholder'] = "Radiographer 1 Name (Optional)"
       self.fields['radiographer2'].label = "Radiographer 2"
       self.fields['radiographer2'].widget.attrs['placeholder'] = "Radiographer 2 Name (Optional)"
       self.fields['radiographer3'].label = "Radiographer 3"
       self.fields['radiographer3'].widget.attrs['placeholder'] = "Radiographer 3 Name (Optional)"
       self.fields['staffname1'].label = "Staff 1 Name"
       self.fields['staffname1'].widget.attrs['placeholder'] = "Staff 1 Name (Optional)"
       self.fields['staffname2'].label = "Staff 2 Name"
       self.fields['staffname2'].widget.attrs['placeholder'] = "Staff 2 Name (Optional)"
       self.fields['staffname3'].label = "Staff 3 Name"
       self.fields['staffname3'].widget.attrs['placeholder'] = "Staff 3 Name (Optional)"
       self.fields['staffname4'].label = "Staff 4 Name"
       self.fields['staffname4'].widget.attrs['placeholder'] = "Staff 4 Name (Optional)"
       self.fields['staffname5'].label = "Staff 5 Name"
       self.fields['staffname5'].widget.attrs['placeholder'] = "Staff 5 Name (Optional)"
       self.fields['staffdesignation1'].label = "Staff 1 Designation"
       self.fields['staffdesignation1'].widget.attrs['placeholder'] = "Staff 1 Designation (Optional)"
       self.fields['staffdesignation2'].label = "Staff 2 Designation"
       self.fields['staffdesignation2'].widget.attrs['placeholder'] = "Staff 2 Designation (Optional)"
       self.fields['staffdesignation3'].label = "Staff 3 Designation"
       self.fields['staffdesignation3'].widget.attrs['placeholder'] = "Staff 3 Designation (Optional)"
       self.fields['staffdesignation4'].label = "Staff 4 Designation"
       self.fields['staffdesignation4'].widget.attrs['placeholder'] = "Staff 4 Designation (Optional)"
       self.fields['staffdesignation5'].label = "Staff 5 Designation"
       self.fields['staffdesignation5'].widget.attrs['placeholder'] = "Staff 5 Designation (Optional)"
       self.fields['radiographer_in_charge_license_no'].label = "R.I.C License No"
       self.fields['radiographer_in_charge_license_no'].widget.attrs['placeholder'] = "R.I.C License No (Required)"
       self.fields['radiographer1_license_no'].label = "Radiographer 1 License No"
       self.fields['radiographer1_license_no'].widget.attrs['placeholder'] = "Radiographer 1 License No (Optional)"
       self.fields['radiographer2_license_no'].label = "Radiographer 2 License No"
       self.fields['radiographer2_license_no'].widget.attrs['placeholder'] = "Radiographer 2 License No (Optional)"
       self.fields['radiographer3_license_no'].label = "Radiographer 3 License No"
       self.fields['radiographer3_license_no'].widget.attrs['placeholder'] = "Radiographer 3 License No (Optional)"
       self.fields['radiographer_in_charge_passport'].label = "R.I.C Passport* (Required) - .jpg,.jpeg,.png"
       self.fields['radiographer_in_charge_passport'].widget.attrs['placeholder'] = "Upload Passport of Radiographer In Charge"
       self.fields['radiographer_in_charge_nysc'].label = "R.I.C NYSC Certificate (Optional)"
       self.fields['radiographer_in_charge_nysc'].widget.attrs['placeholder'] = "Upload NYSC Certificate of Radiographer In Charge"
       self.fields['radiographer_in_charge_practice_license'].label = "R.I.C Practice License* (Required)"
       self.fields['radiographer_in_charge_practice_license'].widget.attrs['placeholder'] = "Upload Practice License of Radiographer In Charge"
       self.fields['radiographer1_practice_license'].label = "Radiographer 1 Practice License (Optional)"
       self.fields['radiographer1_practice_license'].widget.attrs['placeholder'] = "Upload Radiographer 1 Practice License"
       self.fields['radiographer2_practice_license'].label = "Radiographer 2 Practice License(Optional)"
       self.fields['radiographer2_practice_license'].widget.attrs['placeholder'] = "Upload Radiographer 2 Practice License"
       self.fields['radiographer3_practice_license'].label = "Radiographer 3 Practice License(Optional)"
       self.fields['radiographer3_practice_license'].widget.attrs['placeholder'] = "Upload Radiographer 3 Practice License"
       self.fields['cac_certificate'].label = "CAC Certificate* (Required)"
       self.fields['cac_certificate'].widget.attrs['placeholder'] = "Enter CAC Certificate"
       #self.fields['practice_license1'].label = "Practice License"
       #self.fields['practice_license1'].widget.attrs['placeholder'] = "Enter Practice License"
       #self.fields['practice_license2'].label = "Practice License"
       #self.fields['practice_license2'].widget.attrs['placeholder'] = "Enter Practice License"
       self.fields['form_c07'].label = "Form C07* (Required)"
       self.fields['form_c07'].widget.attrs['placeholder'] = "Enter Form C07"





class PaymentDetailsModelForm(forms.ModelForm):
    payment_method = forms.ChoiceField(choices = PAYMENT_METHOD, widget=forms.Select(), required=True)

    class Meta:
        model = Payment
        fields = ('application_no', 'hospital', 'hospital_name', 'rrr_number', 'payment_amount', 'payment_method',  'payment_receipt',)
                                                                                                                                                    
        widgets = {
            'hospital_name': forms.HiddenInput(), 
            'hospital': forms.HiddenInput(), 
            'application_no': forms.TextInput(attrs={'readonly': True}),  
                                
            }

    def __init__(self, *args, **kwargs):
       super(PaymentDetailsModelForm, self).__init__(*args, **kwargs)
       self.fields['application_no'].label = "Application No"
       #self.fields['application_no'].label_from_instance = lambda obj: "{}".format(obj.application_no)
       #self.fields['application_no'].widget.attrs['readonly'] = 'readonly'
       #self.fields['hospital_name'].label = "Hospital Name"
       self.fields['rrr_number'].label = "RRR Number"
       # self.fields['receipt_number'].label = "Receipt Number"
       self.fields['payment_amount'].label = "Payment Amount"
       self.fields['payment_method'].label = "Payment Method"
       self.fields['payment_receipt'].label = "Payment Receipt"

 

   


class ReceiptUploadModelForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('payment_receipt',)

        