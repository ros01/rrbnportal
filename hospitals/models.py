from django.db import models
import uuid
from multiselectfield import MultiSelectField
from datetime import datetime
from django.utils import timezone
from django.urls import reverse
from .choices import STATE_CHOICES, EQUIPMENT, INSPECTION_ZONE, SERVICES, PAYMENT_METHOD, LICENSE_STATUS, VISITATION_REASON
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Hospital
from django.conf import settings
from datetime import datetime
from datetime import date



def increment_application_no():
    last_application_no = Document.objects.all().order_by('application_no').last()
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



class Document(models.Model):

    EQUIPMENT = (
        ('Ultrasound', 'Ultrasound' ),
        ('Conventional X-ray', 'Conventional X-ray'),
        ('Conventional X-ray with Fluoroscopy', 'Conventional X-ray with Fluoroscopy' ),
        ('CT Scan', 'CT Scan' ),
        ('C-Arm/O-ARM', 'C-Arm/O-ARM' ),
        ('MRI', 'MRI'),
        ('Mamography', 'Mamography' ),
        ('Angiography', 'Angiography'),
        ('Dental X-ray', 'Dental X-ray' ),
        ('Echocardiography', 'Echocardiography'),
        ('Radiotherapy', 'Radiotherapy'),
        ('Nuclear Medicine', 'Nuclear Medicine'),
        )

    HOSPITAL_TYPE = (
        ('Diagnostic only', 'Diagnostic only' ),
        ('Therapeutic only', 'Therapeutic only'),
        ('Diagnostic and Therapeutic', 'Diagnostic and Therapeutic'),
        )


    APPLICATION_TYPE = (
        ('New Registration - Radiography Practice Permit', 'New Registration - Radiography Practice Permit' ),
        ('New Registration - Private Hospital Internship', 'New Registration - Private Hospital Internship' ),
        ('New Registration - Government Hospital Internship', 'New Registration - Government Hospital Internship' ),
        ('Renewal - Radiography Practice Permit', 'Renewal - Radiography Practice Permit'),
        ('Renewal - Private Hospital Internship', 'Renewal - Private Hospital Internship'),
        ('Renewal - Government Hospital Internship', 'Renewal - Government Hospital Internship'),
        )

    STATE_CHOICES = (
        ('Abia', 'Abia' ),
        ('Adamawa', 'Adamawa'),
        ('Akwa Ibom', 'Akwa Ibom'),
        ('Anambra', 'Anambra'),
        ('Bauchi', 'Bauchi'),
        ('Bayelsa', 'Bayelsa'),
        ('Benue', 'Benue'),
        ('Borno', 'Borno'),
        ('Cross River', 'Cross River'),
        ('Delta', 'Delta'),
        ('Ebonyi', 'Ebonyi'),
        ('Enugu', 'Enugu'),
        ('Edo' , 'Edo'),
        ('Ekiti', 'Ekiti'),
        ('FCT', 'FCT'),
        ('Gombe', 'Gombe'),
        ('Imo', 'Imo'),
        ('Jigawa', 'Jigawa'),
        ('Kaduna', 'Kaduna'),
        ('Kano', 'Kano'),
        ('Kebbi', 'Kebbi'),
        ('Kogi' , 'Kogi'),
        ('Kwara', 'Kwara'),
        ('Lagos', 'Lagos'),
        ('Nasarawa', 'Nasarawa'),
        ('Niger', 'Niger'),
        ('Ogun', 'Ogun'),
        ('Ondo', 'Ondo'),
        ('Osun', 'Osun'),
        ('Oyo', 'Oyo'),
        ('Plateau', 'Plateau'),
        ('Rivers', 'Rivers'),
        ('Sokoto', 'Sokoto'),
        ('Taraba', 'Taraba'),
        ('Yobe', 'Yobe'),
        ('Zamfara', 'Zamfara'),
        )

    #LICENSE_TYPE = (
        #('Radiography Practice', 'Radiography Practice'),
        #('Internship Accreditation', 'Internship Accreditation'),
        #)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=500, unique=True, null=True, blank=True, 
        default=increment_application_no)
    license_type = models.CharField(max_length=100)
    application_type = models.CharField(max_length=100, choices = APPLICATION_TYPE, blank=True)
    application_status = models.IntegerField(default=1)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospitals', on_delete=models.CASCADE)
    hospital_type = models.CharField(max_length=100, choices = HOSPITAL_TYPE)
    facility_address = models.TextField(blank=True)
    facility_state_of_location = models.CharField(max_length=100, choices = STATE_CHOICES)
    equipment = MultiSelectField(choices = EQUIPMENT)
    radiographer_in_charge = models.CharField(max_length=100)
    radiographer1 = models.CharField(max_length=100, blank=True, null =True)
    radiographer2 = models.CharField(max_length=100, blank=True, null =True)
    radiographer3 = models.CharField(max_length=100, blank=True, null =True)
    radiographer_in_charge_license_no = models.CharField(max_length=100)
    radiographer1_license_no = models.CharField(max_length=100, blank=True, null =True)
    radiographer2_license_no = models.CharField(max_length=100, blank=True, null =True)
    radiographer3_license_no = models.CharField(max_length=100, blank=True, null =True)
    staffname1 = models.CharField(max_length=100, blank=True, null =True)
    staffname2 = models.CharField(max_length=100, blank=True, null =True)
    staffname3 = models.CharField(max_length=100, blank=True, null =True)
    staffname4 = models.CharField(max_length=100, blank=True, null =True)
    staffname5 = models.CharField(max_length=100, blank=True, null =True)
    staffdesignation1 = models.CharField(max_length=100, blank=True, null =True)
    staffdesignation2 = models.CharField(max_length=100, blank=True, null =True)
    staffdesignation3 = models.CharField(max_length=100, blank=True, null =True)
    staffdesignation4 = models.CharField(max_length=100, blank=True, null =True)
    staffdesignation5 = models.CharField(max_length=100, blank=True, null =True)
    radiographer_in_charge_passport = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    radiographer_in_charge_nysc = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    radiographer_in_charge_practice_license = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    radiographer1_practice_license = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    radiographer2_practice_license = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    radiographer3_practice_license = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    cac_certificate = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    form_c07 = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    submission_date = models.DateField(default=date.today)

    class Meta:
        unique_together = ('application_no', 'hospital_name')
       

    def __str__(self):
        return  str(self.hospital_name)

    def equipment_count(self):
        equipment_count = self.equipment
        equipment_count = len(equipment_count)
        return equipment_count

    

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital = models.ForeignKey(Document, null=True, related_name='hospital', on_delete=models.CASCADE)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospitals_py', on_delete=models.CASCADE)
    #hospital_admin = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    application_status = models.IntegerField(default=2)
    rrr_number = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=100)
    payment_amount = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100, choices = PAYMENT_METHOD)
    payment_receipt = models.FileField(upload_to='%Y/%m/%d/')
    payment_date = models.DateField(default=date.today)  
    vet_status = models.IntegerField(default=1)
    vetting_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='vetted_by', blank=True, null=True)
    vet_date =models.DateField(null=True, blank=True, auto_now=True, auto_now_add=False)


    class Meta:
        unique_together = ('application_no','hospital_name')


    def __str__(self):
        return  str(self.hospital_name)

    def save(self, *args, **kwargs):
        
        if self.vet_status == 2:
            self.vet_date = datetime.now()
        super(Payment, self).save(*args, **kwargs)


    def vet_date_pretty(self):
        return self.vet_date.strftime('%b %e %Y')



class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital = models.ForeignKey(Document, null=True, related_name='hospital_dc', on_delete=models.CASCADE)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_py', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, null=True, related_name='payment_py', on_delete=models.CASCADE)
    application_status = models.IntegerField(default=4)
    inspection_scheduler = models.CharField(max_length=300)
    inspection_schedule_date = models.DateField(default=date.today)
    inspection_date = models.DateField(default=date.today)
    inspection_report_deadline = models.DateField(default=date.today)
    inspection_zone = models.CharField(max_length=100, choices = INSPECTION_ZONE)
    nuclear_medicine_total = models.IntegerField(blank=True, null=True)
    carm_total = models.IntegerField(blank=True, null=True)
    radiotherapy_total = models.IntegerField(blank=True, null=True)
    mri_total = models.IntegerField(blank=True, null=True)
    ultrasound_total = models.IntegerField(blank=True, null=True)
    ctscan_total = models.IntegerField(blank=True, null=True)
    xray_total = models.IntegerField(blank=True, null=True)
    flouroscopy_total = models.IntegerField(blank=True, null=True)
    mamography_total = models.IntegerField(blank=True, null=True)
    echocardiography_total = models.IntegerField(blank=True, null=True)
    dentalxray_total = models.IntegerField(blank=True, null=True)
    angiography_total = models.IntegerField(blank=True, null=True)


    class Meta:
        unique_together = ('application_no','hospital_name')

    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Schedule, self).save(*args, **kwargs)
        self.payment.vet_status = 4
        self.payment.save()



class Ultrasound(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_3', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_3', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')


    def __str__(self):
        return str(self.hospital_name)


    def save(self, *args, **kwargs):
        super(Ultrasound, self).save(*args, **kwargs)
        self.schedule.ultrasound_total = self.ultrasound_total
        self.schedule.save()
    
class Nuclearmedicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_4', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_4', on_delete=models.CASCADE)
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


    class Meta:
        unique_together = ('application_no','hospital_name')

    def __str__(self):
        return str(self.hospital_name)


    def save(self, *args, **kwargs):
        super(Nuclearmedicine, self).save(*args, **kwargs)
        self.schedule.nuclear_medicine_total = self.nuclear_medicine_total
        self.schedule.save()

class Radiotherapy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_5', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_5', on_delete=models.CASCADE)
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


    class Meta:
        unique_together = ('application_no','hospital_name')

    def __str__(self):
        return str(self.hospital_name)


    def save(self, *args, **kwargs):
        super(Radiotherapy, self).save(*args, **kwargs)
        self.schedule.radiotherapy_total = self.radiotherapy_total
        self.schedule.save()

class Mri(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_6', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_6', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')

    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Mri, self).save(*args, **kwargs)
        self.schedule.mri_total = self.mri_total
        self.schedule.save()


class Ctscan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_7', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_7', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')

    def __str__(self):
        return str(self.hospital_name)


    def save(self, *args, **kwargs):
        super(Ctscan, self).save(*args, **kwargs)
        self.schedule.ctscan_total = self.ctscan_total
        self.schedule.save()

    
class Xray(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_8', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_8', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')


    def __str__(self):
        return str(self.hospital_name)


    def save(self, *args, **kwargs):
        super(Xray, self).save(*args, **kwargs)
        self.schedule.xray_total = self.xray_total
        self.schedule.save()

    
class Flouroscopy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_9', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_9', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')

    
    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Flouroscopy, self).save(*args, **kwargs)
        self.schedule.flouroscopy_total = self.flouroscopy_total
        self.schedule.save()

class Mamography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_10', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_10', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')

    
    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Mamography, self).save(*args, **kwargs)
        self.schedule.mamography_total = self.mamography_total
        self.schedule.save()


class Echocardiography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_11', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_11', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')

    
    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Echocardiography, self).save(*args, **kwargs)
        self.schedule.echocardiography_total = self.echocardiography_total
        self.schedule.save()


class Dentalxray(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_12', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_12', on_delete=models.CASCADE)
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
    dentalxray_total = models.IntegerField(blank=False, null=False)

    class Meta:
        unique_together = ('application_no','hospital_name')

    
    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Dentalxray, self).save(*args, **kwargs)
        self.schedule.dentalxray_total = self.dentalxray_total
        self.schedule.save()


class Angiography(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_13', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_13', on_delete=models.CASCADE)
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
    angiography_total = models.IntegerField(blank=False, null=False)

    class Meta:
        unique_together = ('application_no','hospital_name')

    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Angiography, self).save(*args, **kwargs)
        self.schedule.angiography_total = self.angiography_total
        self.schedule.save()

   

class Carm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_14', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_14', on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('application_no','hospital_name')

    
    def __str__(self):
        return str(self.hospital_name)

    def save(self, *args, **kwargs):
        super(Carm, self).save(*args, **kwargs)
        self.schedule.carm_total = self.carm_total
        self.schedule.save()

class Inspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_1', on_delete=models.CASCADE)
    hospital = models.ForeignKey(Document, null=True, related_name='hospital_2', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, null=True, related_name='payment_2', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_2', on_delete=models.CASCADE)
    application_status = models.IntegerField(default=5)
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

    class Meta:
        unique_together = ('application_no','hospital_name')

    def __str__(self):
        return str (self.hospital_name)
     
    def save(self, *args, **kwargs):
        #super(Inspection, self).save(*args, **kwargs)
        
        score = []

        if self.schedule.ultrasound_total != None:
            score.insert(0, self.schedule.ultrasound_total)

        if self.schedule.nuclear_medicine_total != None:
            score.insert(0, self.schedule.nuclear_medicine_total)

        if self.schedule.radiotherapy_total != None:
            score.insert(0, self.schedule.radiotherapy_total)
        
        if self.schedule.mri_total != None:
            score.insert(0, self.schedule.mri_total)

        if self.schedule.ctscan_total != None:
            score.insert(0, self.schedule.ctscan_total)

        if self.schedule.xray_total != None:
            score.insert(0, self.schedule.xray_total)

        if self.schedule.flouroscopy_total != None:
            score.insert(0, self.schedule.flouroscopy_total)

        if self.schedule.mamography_total != None:
            score.insert(0, self.schedule.mamography_total)

        if self.schedule.angiography_total != None:
            score.insert(0, self.schedule.angiography_total)

        if self.schedule.echocardiography_total != None:
            score.insert(0, self.schedule.echocardiography_total)
        
        if self.schedule.dentalxray_total != None:
            score.insert(0, self.schedule.dentalxray_total)

        if self.schedule.carm_total != None:
            score.insert(0, self.schedule.carm_total)
        
     
        
        self.inspection_total = sum(score)/len(score)
        super(Inspection, self).save(*args, **kwargs)
        self.schedule.application_status = 5
        self.schedule.save()

        
       

        


class Appraisal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_status = models.IntegerField(default=5)
    appraisal_status = models.IntegerField(default=1)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_16', on_delete=models.CASCADE)
    hospital = models.ForeignKey(Document, null=True, related_name='hospital_16', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, null=True, related_name='payment_16', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_16', on_delete=models.CASCADE)
    vet_status = models.IntegerField(default=4)
    inspection_status = models.IntegerField(default=1)
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

    class Meta:
        unique_together = ('application_no','hospital_name')


    def __str__(self):
        return str (self.hospital_name)

    def save(self, *args, **kwargs):
        super(Appraisal, self).save(*args, **kwargs)
        self.schedule.application_status = 5
        self.schedule.save()

        
class License(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_no = models.CharField(max_length=100)
    hospital_name = models.ForeignKey(Hospital, null=True, related_name='hospital_15', on_delete=models.CASCADE)
    hospital = models.ForeignKey(Document, null=True, related_name='hospital_15', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, null=True, related_name='payment_15', on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, null=True, related_name='schedule_15', on_delete=models.CASCADE)
    inspection = models.ForeignKey(Inspection, null=True, blank=True, related_name='inspection_15', on_delete=models.CASCADE)
    appraisal = models.ForeignKey(Appraisal, null=True, blank=True, related_name='appraisal_15', on_delete=models.CASCADE)
    hospital_code = models.CharField(max_length=500, null=True, blank=True, 
        default=increment_hospital_code)
    application_status = models.IntegerField(default=8)
    license_no = models.CharField(max_length=500, unique=True, null=True, blank=True)
    issue_date = models.DateField(default=date.today)
    expiry_date = models.DateField(default=date.today)
    license_status = models.CharField(max_length=10)
    license_class = models.CharField(max_length=200)


    #def get_absolute_url(self):
        #return reverse("monitoring:issued_license_details", kwargs={"id": self.id})

    class Meta:
        unique_together = (('application_no','hospital_name'), ('application_no','license_no'))
        
    def __str__(self):
        return str(self.application_no)


    def save(self, *args, **kwargs):
        
        #now = datetime.now(timezone.utc)
        
        if self.expiry_date  > date.today():
            self.license_status = "Active"
        else:
            self.license_status = "Expired"
         
            
        super(License, self).save(*args, **kwargs)

        if self.appraisal:
            self.appraisal.application_status = 8
            self.appraisal.save()


        if self.inspection:
            self.inspection.application_status = 8
            self.inspection.save()


        if self.payment:
            self.payment.application_status = 8
            self.payment.save()

        

        


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



