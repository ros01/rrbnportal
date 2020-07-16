from django.db import models
import uuid
from multiselectfield import MultiSelectField
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from .choices import STATE_CHOICES, INSPECTION_ZONE, EQUIPMENT, SERVICES, PAYMENT_METHOD, LICENSE_STATUS, VISITATION_REASON, HOSPITAL_TYPE
from django.db.models.signals import post_save
from django.dispatch import receiver



def increment_application_no():
    last_application_no = Registration.objects.all().order_by('id').last()
    if not last_application_no:
        return '1000'
    application_no = last_application_no.application_no
    new_application_no = str(int(application_no) + 1)
    new_application_no = application_no[0:-(len(new_application_no))] + new_application_no
    return new_application_no


def increment_hospital_code():
    last_hospital_code = License.objects.all().order_by('id').last()
    if not last_hospital_code:
        return '10010000'
    hospital_code = last_hospital_code.hospital_code
    new_hospital_code = str(int(hospital_code) + 1)
    new_hospital_code = hospital_code[0:-(len(new_hospital_code))] + new_hospital_code
    return new_hospital_code


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=500, null=True, blank=True, 
        default=increment_application_no)
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
    radiographers = models.TextField(blank=True)
    radiologists = models.TextField(blank=True, null=
        True)
    reg_date = models.DateTimeField(default=datetime.now, blank=True)
    cac_certificate = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    practice_license1 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    practice_license2 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    form_c07 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)


    def __str__(self):
        return  str (self.hospital_name)

    def reg_date_pretty(self):
        return self.reg_date.strftime('%b %e %Y')

    def get_absolute_url(self):
	    return reverse("hospitals:hospital_details", kwargs={"id": self.id})



class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    rrr_number = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=100)
    payment_amount = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=10, choices = PAYMENT_METHOD)
    payment_receipt = models.FileField(upload_to='%Y/%m/%d/')
    payment_date = models.DateTimeField(default=datetime.now, blank=True)  
    vet_status = models.IntegerField(default=1)
    vetting_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='vetted_by', blank=True, null=True)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    vet_status = models.IntegerField(default=3)
    radiographers = models.CharField(default="Malachy Owakwe", max_length=300)
    radiologists = models.CharField(default="Malachy Owakwe", max_length=300, blank=True, null=
        True)
    inspection_scheduler = models.CharField(max_length=300)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_report_deadline = models.DateTimeField(default=datetime.now, blank=True)
    inspection_zone = models.CharField(max_length=100, choices = INSPECTION_ZONE)

    def __str__(self):
        return self.hospital_name

    def inspection_date_pretty(self):
        return self.inspection_date.strftime('%b %e %Y')

    def inspection_report_deadline_pretty(self):
        return self.inspection_report_deadline.strftime('%b %e %Y')

    def inspection_schedule_date_pretty(self):
        return self.inspection_schedule_date.strftime('%b %e %Y')


class Inspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    equipment = models.CharField(max_length=300)
    radiographers = models.CharField(max_length=300)
    radiologists = models.CharField(max_length=300)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_report_deadline = models.DateTimeField(default=datetime.now, blank=True)
    inspection_status = models.IntegerField(default=1)
    shielding_score = models.IntegerField()
    equipment_layout_score = models.IntegerField()
    radiographer_no_score = models.IntegerField()
    radiologist_certification_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    personnel_monitoring_score = models.IntegerField()
    room_adequacy_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    accessories_score = models.IntegerField()
    warning_light_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    functional_equipment_score = models.IntegerField()
    equipment_installation_score = models.IntegerField()
    darkroom_score = models.IntegerField()
    public_safety_score = models.IntegerField()
    inspection_total = models.IntegerField()
    inspection_comments = models.TextField(blank=True)
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


class Appraisal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    equipment = models.CharField(max_length=300)
    radiographers = models.CharField(max_length=300)
    radiologists = models.CharField(max_length=300, blank=True, null=
        True)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_report_deadline = models.DateTimeField(default=datetime.now, blank=True)
    inspection_status = models.IntegerField(default=1)
    radiographers_score = models.IntegerField()
    radiologists_score = models.IntegerField()
    darkroom_technicians_score = models.IntegerField()
    offices_score = models.IntegerField()
    library_score = models.IntegerField()
    call_room_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    toilets_score = models.IntegerField()
    static_xray_score = models.IntegerField()
    mobile_xray_score = models.IntegerField()
    ct_score = models.IntegerField()
    mri_score = models.IntegerField()
    fluoroscopy_score = models.IntegerField()
    nuclear_medicine_score = models.IntegerField()
    radiation_therapy_score = models.IntegerField()
    ultrasound_score = models.IntegerField()
    mammography_score = models.IntegerField()
    dental_equipment_score = models.IntegerField()
    carm_score = models.IntegerField()
    processing_room_score = models.IntegerField()
    diagnostic_room_score = models.IntegerField()
    personnel_monitoring_score = models.IntegerField()
    warning_light_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    cpds_score = models.IntegerField()
    departmental_seminars_score = models.IntegerField()
    licence_status_score = models.IntegerField()
    appraisal_total = models.IntegerField()
    appraisal_comments = models.TextField(blank=True)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_code = models.CharField(max_length=500, null=True, blank=True, 
        default=increment_hospital_code)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    license_type = models.CharField(max_length=200)
    license_no = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    issue_date = models.DateTimeField(default=datetime.now, blank=True)
    expiry_date = models.DateTimeField(default=datetime.now, blank=True)
    license_status = models.CharField(max_length=10, choices = LICENSE_STATUS)



    def get_absolute_url(self):
        return reverse("monitoring:license_issued", kwargs={"id": self.id})
    
    def __str__(self):
        return self.license_no


    def issue_date_pretty(self):
        return self.issue_date.strftime('%b %e %Y')


    def expiry_date_pretty(self):
        return self.expiry_date.strftime('%b %e %Y')


class Records(models.Model):
    hospital_name = models.CharField(max_length=200)
    hospital_type = models.CharField(max_length=100, choices = HOSPITAL_TYPE)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    state = models.CharField(max_length=100, choices = STATE_CHOICES)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    services = models.CharField(max_length=100, choices = SERVICES)
    equipment = MultiSelectField(choices = EQUIPMENT)
    radiographers = models.TextField(blank=True, null=
        True)
    radiologists = models.TextField(blank=True, null=
        True)
    visitation_reason = models.CharField(max_length=100, choices = VISITATION_REASON)
    visitation_comments = models.TextField(blank=True)
    date_visited = models.DateTimeField(default=datetime.now, blank=True)
    next_visitation_date = models.DateTimeField(default=datetime.now, blank=True)
    cac_certificate = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    practice_license = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    form_c07 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)


    def __str__(self):
        return  str (self.hospital_name)

    def date_visited_pretty(self):
        return self.date_visited.strftime('%b %e %Y')












