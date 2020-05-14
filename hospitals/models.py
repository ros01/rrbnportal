from django.db import models
from multiselectfield import MultiSelectField
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from .choices import STATE_CHOICES
from .choices import EQUIPMENT
from .choices import SERVICES
from django.db.models.signals import post_save
from django.dispatch import receiver


class Registration(models.Model):
    EQUIPMENT = (
        ('Ultrasound', 'Ultrasound' ),
        ('X-ray', 'X-ray'),
        ('CT Scan', 'CT Scan' ),
        ('MRI', 'MRI'),
        ('Mamography', 'Mamography' ),
        ('Angiography', 'Angiography'),
        ('Dental Radiography', 'Dental Radiography' ),
        ('Echocardiography', 'Echocardiography'),
        ('Linac', 'Linac'),
        ('Cobalt 60', 'Cobalt 60'),
        ('Nuclear Medicine', 'Nuclear Medicine'),
        )


    id = models.IntegerField(max_length=6, primary_key=True, unique=True, default=10000)
    #id = models.AutoField(primary_key=True, unique=True)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
    vet_status = models.IntegerField(default=1)
    
    


    def __str__(self):
        return  str (self.id)



    def reg_date_pretty(self):
        return self.reg_date.strftime('%b %e %Y')


    def get_absolute_url(self):
	    return reverse("hospitals:update", kwargs={"id": self.id})



class Payment(models.Model):
    application_no = models.CharField(max_length=200)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    rrr_number = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=100)
    payment_amount = models.CharField(max_length=100)
    
    PAYMENT_METHOD = (
        ('Bank', 'Bank'),
        
        )

    payment_method = models.CharField(max_length=10, choices = PAYMENT_METHOD)

    payment_receipt = models.FileField(upload_to='%Y/%m/%d/', blank=True)
    payment_date = models.DateTimeField(default=datetime.now, blank=True)
    status = models.CharField(max_length=30)

    #def __str__(self):
     #   return self.hospital_name


    def __str__(self):
        return self.hospital_name



    def payment_date_pretty(self):
        return self.payment_date.strftime('%b %e %Y')


    def get_absolute_url(self):
	    return reverse("hospitals:payment_update", kwargs={"id": self.id})


class Inspection(models.Model):
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_status = models.CharField(max_length=100)
    inspection_score = models.IntegerField()
    shielding = models.IntegerField()
    equipment = models.IntegerField()
    radiographer_adequacy = models.IntegerField()
    radiographer_license = models.IntegerField()
    personnel_monitoring = models.IntegerField()
    room_size = models.IntegerField()
    water_supply = models.IntegerField()
    C07_form = models.IntegerField()
    darkroom = models.IntegerField()
    safety = models.IntegerField()
    photo_main = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)
    photo_1 = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)
    photo_5 = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)
    photo_6 = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)


    def __str__(self):
        return self.hospital_name

    def inspection_date_pretty(self):
        return self.inspection_date.strftime('%b %e %Y')

    def inspection_score(self):
        return self.shielding

    def get_absolute_url(self):
	    return reverse("hospitals:update", kwargs={"id": self.id})


class License(models.Model):
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    license_no = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    issue_date = models.DateTimeField(default=datetime.now, blank=True)
    expiry_date = models.DateTimeField(default=datetime.now, blank=True)
    VALIDITY = (
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        )
    validity = models.CharField(max_length=10, choices = VALIDITY)
    def __str__(self):
        return self.license_no









