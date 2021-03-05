from django import forms
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import Document, Payment
from .choices import STATE_CHOICES, SERVICES, EQUIPMENT, PAYMENT_METHOD
from django.forms.widgets import CheckboxSelectMultiple
from django.forms import MultipleChoiceField
from django.forms.models import ModelMultipleChoiceField
from django.forms import MultipleChoiceField
from django.contrib.auth import get_user_model
User = get_user_model()




class HospitalDetailModelForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('license_type', 'application_type', 'hospital_name', 'hospital_type', 'equipment', 'radiographers', 'radiologists', 'cac_certificate', 'practice_license1', 'practice_license2', 'form_c07')

        widgets = {
            'radiographers': forms.Textarea(attrs={'rows':3, 'cols':5}), 
            'radiologists': forms.Textarea(attrs={'rows':3, 'cols':5}),
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
       self.fields['equipment'].label = "Available Equipment"
       self.fields['equipment'].widget = CheckboxSelectMultiple()
       self.fields['radiographers'].label = "Radiographers"
       self.fields['radiographers'].widget.attrs['placeholder'] = "Enter Radiographers"
       self.fields['radiologists'].label = "Radiologists"
       self.fields['radiologists'].widget.attrs['placeholder'] = "Enter Radiologists"
       self.fields['cac_certificate'].label = "CAC Certificate"
       self.fields['cac_certificate'].widget.attrs['placeholder'] = "Enter CAC Certificate"
       self.fields['practice_license1'].label = "Practice License"
       self.fields['practice_license1'].widget.attrs['placeholder'] = "Enter Practice License"
       self.fields['practice_license2'].label = "Practice License"
       self.fields['practice_license2'].widget.attrs['placeholder'] = "Enter Practice License"
       self.fields['form_c07'].label = "Form C07"
       self.fields['form_c07'].widget.attrs['placeholder'] = "Enter Form C07"





class PaymentDetailsModelForm(forms.ModelForm):
    payment_method = forms.ChoiceField(choices = PAYMENT_METHOD, widget=forms.Select(), required=True)

    class Meta:
        model = Payment
        fields = ('application_no', 'hospital', 'hospital_name', 'rrr_number', 'receipt_number',  'payment_amount', 'payment_method',  'payment_receipt',)
                                                                                                                                                    
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
       self.fields['receipt_number'].label = "Receipt Number"
       self.fields['payment_amount'].label = "Payment Amount"
       self.fields['payment_method'].label = "Payment Method"
       self.fields['payment_receipt'].label = "Payment Receipt"

 

   


class ReceiptUploadModelForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('payment_receipt',)

        