from django.db import models
from multiselectfield import MultiSelectField
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from .choices import STATE_CHOICES, INSPECTION_ZONE, EQUIPMENT, SERVICES, PAYMENT_METHOD, SCORE, LICENSE_STATUS
from django.db.models.signals import post_save
from django.dispatch import receiver


class Registration(models.Model):
    id = models.IntegerField(max_length=6, primary_key=True, unique=True, default=10000)
    #id = models.AutoField(primary_key=True, unique=True)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    rc_number = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    state = models.CharField(max_length=100, choices = STATE_CHOICES)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    services = models.CharField(max_length=100, choices = SERVICES)
    equipment = MultiSelectField(choices = EQUIPMENT)
    radiographers = models.CharField(max_length=200, blank=True)
    reg_date = models.DateTimeField(default=datetime.now, blank=True)
    cac_certificate = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    practice_license = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    
    
    


    def __str__(self):
        return  str (self.id)



    def reg_date_pretty(self):
        return self.reg_date.strftime('%b %e %Y')


    def get_absolute_url(self):
	    return reverse("hospitals:update", kwargs={"id": self.id})



class Payment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    application_no = models.CharField(max_length=200)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    state = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    services = models.CharField(max_length=200)
    equipment = models.CharField(max_length=200)
    radiographers = models.CharField(max_length=200)
    rrr_number = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=100)
    payment_amount = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=10, choices = PAYMENT_METHOD)
    payment_receipt = models.FileField(upload_to='%Y/%m/%d/')
    payment_date = models.DateTimeField(default=datetime.now, blank=True)  
    vet_status = models.IntegerField(default=1)
    vetting_officer = models.CharField(max_length=200)
    vet_date =models.DateTimeField(blank=True, auto_now=False, auto_now_add=True)



    def __str__(self):
        return self.hospital_name



    def payment_date_pretty(self):
        return self.payment_date.strftime('%b %e %Y')

    def vet_date_pretty(self):
        return self.vet_date.strftime('%b %e %Y')


    def get_absolute_url(self):
	    return reverse("hospitals:payment_update", kwargs={"id": self.id})

class Schedule(models.Model):

    application_no = models.CharField(max_length=200)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    services = models.CharField(max_length=300)
    equipment = models.CharField(max_length=300)
    radiographers = models.CharField(max_length=300)
    inspection_scheduler = models.CharField(default="Ebere Onwuegbuchu", max_length=300)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_report_deadline = models.DateTimeField(default=datetime.now, blank=True)
    inspection_zone = models.CharField(max_length=100, choices = INSPECTION_ZONE)

    def inspection_date_pretty(self):
        return self.inspection_date.strftime('%b %e %Y')

    def inspection_report_deadline_pretty(self):
        return self.inspection_report_deadline.strftime('%b %e %Y')

    def inspection_schedule_date_pretty(self):
        return self.inspection_schedule_date.strftime('%b %e %Y')


class Inspection(models.Model):
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    equipment = models.CharField(max_length=300)
    radiographers = models.CharField(max_length=300)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_report_deadline = models.DateTimeField(default=datetime.now, blank=True)
    inspection_status = models.IntegerField(default=1)
    shielding = models.CharField(max_length=10, choices = SCORE)
    equipment_layout = models.CharField(max_length=10, choices = SCORE)
    radiographer_adequacy = models.CharField(max_length=10, choices = SCORE)
    radiographer_license = models.CharField(max_length=10, choices = SCORE)
    personnel_monitoring = models.CharField(max_length=10, choices = SCORE)
    room_size = models.CharField(max_length=10, choices = SCORE)
    water_supply = models.CharField(max_length=10, choices = SCORE)
    C07_form_compliance = models.CharField(max_length=10, choices = SCORE)
    darkroom = models.CharField(max_length=10, choices = SCORE)
    public_safety = models.CharField(max_length=10, choices = SCORE)
    functional_equipment = models.CharField(max_length=10, choices = SCORE)
    inspection_scores = models.IntegerField(default=1)
    photo_main = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    photo_1 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    photo_5 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    photo_6 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)


    def __str__(self):
        return self.hospital_name

    def inspection_date_pretty(self):
        return self.inspection_date.strftime('%b %e %Y')



class License(models.Model):
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    license_no = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    issue_date = models.DateTimeField(default=datetime.now, blank=True)
    expiry_date = models.DateTimeField(default=datetime.now, blank=True)
    license_status = models.CharField(max_length=10, choices = LICENSE_STATUS)
    def __str__(self):
        return self.license_no


    def issue_date_pretty(self):
        return self.issue_date.strftime('%b %e %Y')


    def expiry_date_pretty(self):
        return self.expiry_date.strftime('%b %e %Y')










