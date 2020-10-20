from django.db import models
import uuid
from multiselectfield import MultiSelectField
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from .choices import STATE_CHOICES, INSPECTION_ZONE, EQUIPMENT, SERVICES, PAYMENT_METHOD, LICENSE_STATUS, VISITATION_REASON, HOSPITAL_TYPE, APPLICATION_TYPE
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist



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
    application_type = models.CharField(max_length=100, choices = APPLICATION_TYPE)
    application_status = models.IntegerField(default=1)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    #practice_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
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

    def equipment_count(self):
        equipment_count = self.equipment
        equipment_count = len(equipment_count)
        return equipment_count



class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=200)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    #practice_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    application_type = models.CharField(max_length=100)
    application_status = models.IntegerField(default=2)
    license_category = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    state = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    services = models.CharField(max_length=200)
    equipment = models.CharField(max_length=200)
    radiographers = models.TextField(blank=True)
    radiologists = models.TextField(blank=True, null=True)
    rrr_number = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=100)
    payment_amount = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=10, choices = PAYMENT_METHOD)
    payment_receipt = models.FileField(upload_to='%Y/%m/%d/')
    payment_date = models.DateTimeField(default=datetime.now, blank=True)  
    vet_status = models.IntegerField(default=1)
    vetting_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='vetted_by', blank=True, null=True)
    vet_date =models.DateTimeField(blank=True, null=True)



    def __str__(self):
        return self.hospital_name

    def payment_date_pretty(self):
        return self.payment_date.strftime('%b %e %Y')

   


    def save(self, *args, **kwargs):
        
        if self.vet_status == 2:
            self.vet_date = datetime.now()
        super(Payment, self).save(*args, **kwargs)


    def vet_date_pretty(self):
        return self.vet_date.strftime('%b %e %Y')



class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=200)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    #practice_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    application_type = models.CharField(max_length=100)
    application_status = models.IntegerField(default=4)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    services = models.CharField(max_length=300)
    equipment = models.CharField(max_length=300)
    vet_status = models.IntegerField(default=3)
    payment_amount = models.CharField(max_length=100)
    radiographers = models.CharField(max_length=300)
    radiologists = models.CharField(max_length=300, blank=True, null=True)
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

    def save(self, *args, **kwargs):
        super(Schedule, self).save(*args, **kwargs)
        self.practice_manager.payment.vet_status = 4
        self.practice_manager.payment.save()


        

class Nuclearmedicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    nuclear_medicine_physicians_no_score  = models.IntegerField()
    other_staff_no_score  = models.IntegerField() 
    nuclear_medicine_certification_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()  
    prmd_prpe_score = models.IntegerField() 
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    radionuclide_accessories_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField() 
    equipment_installation_location_score = models.IntegerField() 
    radionuclide_storage_unit_score = models.IntegerField() 
    offices_adequacy_score = models.IntegerField() 
    quality_control_score = models.IntegerField()
    rso_score = models.IntegerField() 
    radiation_safety_program_score = models.IntegerField()
    labelling_score = models.IntegerField()
    performance_survey_score = models.IntegerField()
    radioactive_materials_security_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField() 
    waiting_room_score = models.IntegerField() 
    nuclear_medicine_total = models.IntegerField() 

    def __str__(self):
        return str(self.nuclear_medicine_total)

class Radiotherapy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField() 
    radiologists_no_score = models.IntegerField()
    other_staff_score = models.IntegerField()
    radiotherapy_certification_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    rso_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    radiotherapy_accessories_score = models.IntegerField()
    mould_room_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    radiotherapy_total = models.IntegerField()

    def __str__(self):
        return str(self.radiotherapy_total)

class Mri(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    mri_certification_score = models.IntegerField()
    metal_screening_device_score = models.IntegerField()
    screening_questionnaire_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    technical_room_adequacy_score = models.IntegerField()
    mri_total = models.IntegerField()

    def __str__(self):
        return str(self.mri_total)



class Ultrasound(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    ultrasound_qualification_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    support_staff_score = models.IntegerField()
    ultrasound_total = models.IntegerField()


    def __str__(self):
        return str(self.ultrasound_total)
    

class Ctscan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    rso_rsa_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    ctscan_total = models.IntegerField()

    def __str__(self):
        return str(self.ctscan_total)

    


class Xray(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    rso_rsa_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    xray_total = models.IntegerField()


    def __str__(self):
        return str(self.xray_total)

    
class Flouroscopy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    rso_rsa_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    flouroscopy_total = models.IntegerField()

    
    def __str__(self):
        return str(self.flouroscopy_total)

class Mamography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    mammography_certification_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    rso_rsa_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    mamography_total = models.IntegerField()

    
    def __str__(self):
        return str(self.mamography_total)


class Echocardiography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    echocardiography_certification_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    support_staff_score = models.IntegerField()
    echocardiography_total = models.IntegerField()

    
    def __str__(self):
        return str(self.echocardiography_total)


class Dentalxray(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    dentalxray_total = models.IntegerField()

    
    def __str__(self):
        return str(self.dentalxray_total)


class Angiography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    angiography_certification_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    rso_rsa_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    angiography_total = models.IntegerField()

    
    def __str__(self):
        return str(self.angiography_total)


    

class Carm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    shielding_score = models.IntegerField()
    room_design_score = models.IntegerField()
    radiographers_no_score = models.IntegerField()
    radiologists_no_score = models.IntegerField()
    radiographer_license_score = models.IntegerField()
    prmd_prpe_score = models.IntegerField()
    water_supply_score = models.IntegerField()
    equipment_certification_score = models.IntegerField()
    accessories_adequacy_score = models.IntegerField()
    warning_lights_score = models.IntegerField()
    warning_signs_score = models.IntegerField()
    C07_form_compliance_score = models.IntegerField()
    equipment_installation_location_score = models.IntegerField()
    processing_unit_score = models.IntegerField()
    toilets_cleanliness_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    offices_adequacy_score = models.IntegerField()
    carm_total = models.IntegerField()

    
    def __str__(self):
        return str(self.carm_total)


class Inspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    #practice_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    equipment = models.CharField(max_length=300)
    license_category = models.CharField(max_length=200)
    application_status = models.IntegerField(default=5)
    application_type = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    radiographers = models.CharField(max_length=300)
    radiologists = models.CharField(max_length=300)
    payment_amount = models.CharField(max_length=100)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    next_inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_report_deadline = models.DateTimeField(default=datetime.now, blank=True)
    inspection_zone = models.CharField(max_length=100)
    vet_status = models.IntegerField(default=4)
    inspection_status = models.IntegerField(default=1)
    inspection_total = models.DecimalField(blank=True, max_digits=5, decimal_places=2)
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

    


    def save(self, *args, **kwargs):
        #super(Inspection, self).save(*args, **kwargs)
        #self.practice_manager.schedule.application_status=5
        #self.practice_manager.schedule.save()

        #if self.practice_manager.nuclearmedicine.nuclear_medicine_total and self.practice_manager.nuclearmedicine.nuclear_medicine_total

        #score = self.practice_manager.nuclearmedicine.nuclear_medicine_total + self.practice_manager.radiotherapy.radiotherapy_total + self.practice_manager.mri.mri_total + self.practice_manager.ultrasound.ultrasound_total + self.practice_manager.ctscan.ctscan_total + self.practice_manager.xray.xray_total + self.practice_manager.flouroscopy.flouroscopy_total 
        #self.inspection_total = 99
        
        #score = [self.practice_manager.nuclearmedicine.nuclear_medicine_total, self.practice_manager.radiotherapy.radiotherapy_total, self.practice_manager.mri.mri_total, self.practice_manager.ultrasound.ultrasound_total, self.practice_manager.ctscan.ctscan_total, self.practice_manager.xray.xray_total, self.practice_manager.flouroscopy.flouroscopy_total] 
        
        #score = [self.practice_manager.nuclearmedicine.nuclear_medicine_total, self.practice_manager.radiotherapy.radiotherapy_total, self.practice_manager.mri.mri_total, self.practice_manager.ultrasound.ultrasound_total, self.practice_manager.ctscan.ctscan_total, self.practice_manager.xray.xray_total, self.practice_manager.flouroscopy.flouroscopy_total]
        score = []

       
        try:
            score.insert(0, self.practice_manager.nuclearmedicine.nuclear_medicine_total)
        except Nuclearmedicine.DoesNotExist:
            pass
        
        try:
            score.insert(0, self.practice_manager.radiotherapy.radiotherapy_total)
        except Radiotherapy.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.mri.mri_total)
        except Mri.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.ctscan.ctscan_total)
        except Ctscan.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.ultrasound.ultrasound_total)
        except Ultrasound.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.xray.xray_total)
        except Xray.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.flouroscopy.flouroscopy_total)
        except Flouroscopy.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.mamography.mamography_total)
        except Mamography.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.angiography.angiography_total)
        except Angiography.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.echocardiography.echocardiography_total)
        except Echocardiography.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.dentalxray.dentalxray_total)
        except Dentalxray.DoesNotExist:
            pass

        try:
            score.insert(0, self.practice_manager.carm.carm_total)
        except Carm.DoesNotExist:
            pass
      
        
        self.inspection_total = sum(score)/len(score)
        super(Inspection, self).save(*args, **kwargs)
        self.practice_manager.schedule.application_status = 5
        self.practice_manager.schedule.save()

        
       

        


class Appraisal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    practice_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    #practice_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    application_status = models.IntegerField(default=5)
    application_type = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    equipment = models.CharField(max_length=300)
    radiographers = models.CharField(max_length=300)
    radiologists = models.CharField(max_length=300, blank=True, null=
        True)
    appraisal_status = models.IntegerField(default=1)
    payment_amount = models.CharField(max_length=100)
    inspection_schedule_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_report_deadline = models.DateTimeField(default=datetime.now, blank=True)
    next_inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    inspection_status = models.IntegerField(default=1)
    inspection_zone = models.CharField(max_length=100)
    radiographers_score = models.IntegerField()
    radiologists_score = models.IntegerField()
    support_staff_score = models.IntegerField()
    offices_score = models.IntegerField()
    library_score = models.IntegerField()
    call_room_score = models.IntegerField()
    waiting_room_score = models.IntegerField()
    toilets_score = models.IntegerField()
    room_design_score = models.IntegerField() 
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
    processing_unit_score = models.IntegerField()
    diagnostic_room_score = models.IntegerField()
    personnel_score = models.IntegerField()
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
    #practice_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    hospital_name = models.CharField(max_length=200)
    license_category = models.CharField(max_length=200)
    license_type = models.CharField(max_length=200)
    application_status = models.IntegerField(default=8)
    application_type = models.CharField(max_length=100)
    license_no = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    payment_amount = models.CharField(max_length=100)
    inspection_date = models.DateTimeField(default=datetime.now, blank=True)
    issue_date = models.DateTimeField(default=datetime.now, blank=True)
    expiry_date = models.DateTimeField(default=datetime.now, blank=True)
    license_status = models.CharField(max_length=10)



    def get_absolute_url(self):
        return reverse("monitoring:issued_license_details", kwargs={"id": self.id})
    
    def __str__(self):
        return self.license_no

    def inspection_date_pretty(self):
        return self.inspection_date.strftime('%b %e %Y')


    def issue_date_pretty(self):
        return self.issue_date.strftime('%b %e %Y')


    def expiry_date_pretty(self):
        return self.expiry_date.strftime('%b %e %Y')


    def save(self, *args, **kwargs):
        
        now = datetime.now(timezone.utc)
        
        if self.expiry_date > now:
            self.license_status = "Active"
        else:
            self.license_status = "Expired"

            
    
        
        super(License, self).save(*args, **kwargs)
        self.practice_manager.inspection.application_status = 8
        self.practice_manager.inspection.save()





    


class Records(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    state = models.CharField(max_length=100, choices = STATE_CHOICES)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    practice_category = models.CharField(max_length=100, choices = SERVICES)
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
    practice_license1 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    practice_license2 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    form_c07 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    inspection_zone = models.CharField(max_length=100)


    def __str__(self):
        return  str (self.hospital_name)

    def date_visited_pretty(self):
        return self.date_visited.strftime('%b %e %Y')


    #def get_absolute_url(self):
        #return reverse("monitoring:hospital_record_details", kwargs={"id": self.id})












