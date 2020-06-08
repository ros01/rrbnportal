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
         fields = ('practice_manager','hospital_name', 'license_category', 'rc_number', 'phone', 'email',  'city', 'state', 'address', 'services', 'equipment', 'radiographers')
         

         widgets = {'practice_manager': forms.HiddenInput(),}

    def clean_practice_manager(self):
        practice_manager = self.cleaned_data.get('practice_manager')
        qs = Registration.objects.filter(practice_manager=practice_manager)
        if qs.count() > 1:
            raise forms.ValidationError("Hospital details already submitted")
        return practice_manager
        


class CertUploadModelForm(forms.ModelForm):
    class Meta:
    	model = Registration
    	fields = ('cac_certificate', 'practice_license')


class PaymentDetailsModelForm(forms.ModelForm):
    payment_method = forms.ChoiceField(choices = PAYMENT_METHOD, widget=forms.Select(), required=True)

    class Meta:
        model = Payment
        fields = ('practice_manager','hospital_name', 'application_no', 'license_category', 'rrr_number', 'receipt_number',  'payment_amount', 'payment_method',  'payment_date', 'phone', 'email', 'state', 'city', 'address', 'services', 'equipment', 'radiographers', 'payment_receipt',)
                                                                                                                                                    

        widgets = {
        'practice_manager': forms.HiddenInput(),
        'hospital_name': forms.TextInput(attrs={'readonly': True}),
        'application_no': forms.TextInput(attrs={'readonly': True}),
        


        
       
        }


    def __init__(self, *args, **kwargs):
       super(PaymentDetailsModelForm, self).__init__(*args, **kwargs)
       #self.fields['application_no'].widget.attrs['readonly'] = True 
       #self.fields['phone'].widget.attrs['readonly'] = True

 

       #initial = kwargs.get('initial', {})
       #self.application_no = initial.get('application_no')
       #self.phone = initial.get('phone')
       #super(PaymentDetailsModelForm, self).__init__(*args, **kwargs) 


    










class ReceiptUploadModelForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('payment_receipt',)

        