from django import forms
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import Registration, Payment
from .choices import STATE_CHOICES, SERVICES, EQUIPMENT, PAYMENT_METHOD




class BasicDetailModelForm(forms.ModelForm):
    state = forms.ChoiceField(choices = STATE_CHOICES, widget=forms.Select(), required=True)
    services = forms.ChoiceField(choices = SERVICES, widget=forms.Select(), required=True)
    equipment = forms.MultipleChoiceField(choices = EQUIPMENT, widget=forms.CheckboxSelectMultiple())

    class Meta:
         model = Registration
         fields = ('practice_manager','hospital_name', 'application_no', 'application_type', 'license_category', 'rc_number', 'phone', 'email',  'city', 'state', 'address', 'services', 'equipment', 'radiographers', 'radiologists', 'cac_certificate', 'practice_license1', 'practice_license2','form_c07')
         

         widgets = {
         'radiographers': forms.Textarea(attrs={'rows':4, 'cols':12}),
         'radiologists': forms.Textarea(attrs={'rows':4, 'cols':12}),
         'application_no': forms.HiddenInput(),
         'hospital_name': forms.TextInput(attrs={'readonly': True}),
         'phone_no': forms.TextInput(attrs={'readonly': True}),
         'email': forms.TextInput(attrs={'readonly': True}),
         'license_category': forms.TextInput(attrs={'readonly': True}),
         }






    #def clean_practice_manager(self):
        #practice_manager = self.cleaned_data.get('practice_manager')
        #qs = Registration.objects.filter(practice_manager=practice_manager)
        #if qs.count() > 1:
            #raise forms.ValidationError("Hospital details already submitted")
        #return practice_manager

    def __init__(self, *args, **kwargs):
       super(BasicDetailModelForm, self).__init__(*args, **kwargs)
       self.fields['rc_number'].label = "RC Number"
       self.fields['hospital_name'].label = "Hospital Name"
       self.fields['cac_certificate'].label = "CAC Certificate"
       self.fields['practice_license1'].label = "Radiographer Practice License"
       self.fields['practice_license2'].label = "Radiographer Practice License"
       self.fields['form_c07'].label = "Form C07"
        


class CertUploadModelForm(forms.ModelForm):
    class Meta:
    	model = Registration
    	fields = ('cac_certificate', 'practice_license1', 'form_c07')

    def __init__(self, *args, **kwargs):
       super(CertUploadModelForm, self).__init__(*args, **kwargs)
       self.fields['cac_certificate'].label = "CAC Certificate"
       self.fields['practice_license'].label = "Radiographer Practice License"
       self.fields['form_c07'].label = "Form C07"


class PaymentDetailsModelForm(forms.ModelForm):
    payment_method = forms.ChoiceField(choices = PAYMENT_METHOD, widget=forms.Select(), required=True)

    class Meta:
        model = Payment
        fields = ('practice_manager','hospital_name', 'application_no', 'license_category', 'application_type','rrr_number', 'receipt_number',  'payment_amount', 'payment_method',  'payment_date', 'phone', 'email', 'state', 'city', 'address', 'services', 'equipment', 'payment_receipt', 'radiographers', 'radiologists',)
                                                                                                                                                    

        widgets = {
        'practice_manager': forms.HiddenInput(),
        'application_type': forms.HiddenInput(),
        'phone': forms.HiddenInput(),
        'email': forms.HiddenInput(),
        'state': forms.HiddenInput(),
        'city': forms.HiddenInput(),
        'address': forms.HiddenInput(),
        'services': forms.HiddenInput(),
        'equipment': forms.HiddenInput(),
        'radiographers': forms.HiddenInput(),
        'radiologists': forms.HiddenInput(),
        'hospital_name': forms.TextInput(attrs={'readonly': True}),
        'application_no': forms.TextInput(attrs={'readonly': True}),  
        'license_category': forms.TextInput(attrs={'readonly': True}),   
        }



    def __init__(self, *args, **kwargs):
       super(PaymentDetailsModelForm, self).__init__(*args, **kwargs)
       self.fields['application_no'].label = "Application No"
       self.fields['hospital_name'].label = "Hospital Name"
       self.fields['license_category'].label = "License Category"
       self.fields['rrr_number'].label = "RRR Number"
       self.fields['receipt_number'].label = "Receipt Number"
       self.fields['payment_amount'].label = "Payment Amount"
       self.fields['payment_method'].label = "Payment Method"
       self.fields['payment_receipt'].label = "Payment Receipt"

 

   


class ReceiptUploadModelForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('payment_receipt',)

        