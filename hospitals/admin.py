from django.contrib import admin

from .models import Registration, Payment, Inspection, License, Schedule, Records, Appraisal, Ultrasound, Mri, Xray, Ctscan, Flouroscopy, Nuclearmedicine, Radiotherapy, Mamography, Dentalxray, Echocardiography, Angiography


class RegistrationAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'license_category', 'address', 'state',
                  'services', 'radiographers')
  list_display_links = ('application_no', 'hospital_name')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'address', 'state',
                   'services', 'equipment', 'radiographers')
  list_per_page = 25


admin.site.register(Registration, RegistrationAdmin)




class PaymentAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'license_category', 'rrr_number', 'receipt_number', 'payment_amount',
                  'payment_receipt', 'payment_date')
  list_display_links = ('application_no', 'hospital_name')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'receipt_number', 'payment_date',
                  'payment_date')
  list_per_page = 25


admin.site.register(Payment, PaymentAdmin)



class ScheduleAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name',  'address', 'equipment',
   'inspection_date', 'inspection_report_deadline', 'inspection_zone',)
  list_display_links = ('application_no', 'hospital_name', 'inspection_date', 'inspection_zone',)
  list_filter = ('application_no', 'hospital_name', 'inspection_date', 'inspection_zone',)
  search_fields = ('hospital_name', 'application_no','equipment', 'inspection_date', 'inspection_zone',)
  list_per_page = 25


admin.site.register(Schedule, ScheduleAdmin)

class NuclearmedicineAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'nuclear_medicine_total')
  list_display_links = ('id', 'practice_manager', 'nuclear_medicine_total')
  list_filter = ('id', 'practice_manager', 'nuclear_medicine_total')
  search_fields = ('id', 'practice_manager', 'nuclear_medicine_total')
  list_per_page = 25


admin.site.register(Nuclearmedicine, NuclearmedicineAdmin)

class RadiotherapyAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'radiotherapy_total')
  list_display_links = ('id', 'practice_manager', 'radiotherapy_total')
  list_filter = ('id', 'practice_manager', 'radiotherapy_total')
  search_fields = ('id', 'practice_manager', 'radiotherapy_total')
  list_per_page = 25


admin.site.register(Radiotherapy, RadiotherapyAdmin)



class UltrasoundAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'ultrasound_total')
  list_display_links = ('id', 'practice_manager', 'ultrasound_total')
  list_filter = ('id', 'practice_manager', 'ultrasound_total')
  search_fields = ('id', 'practice_manager', 'ultrasound_total')
  list_per_page = 25


admin.site.register(Ultrasound, UltrasoundAdmin)


class MriAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'mri_total')
  list_display_links = ('id', 'practice_manager', 'mri_total')
  list_filter = ('id', 'practice_manager', 'mri_total')
  search_fields = ('id', 'practice_manager', 'mri_total')
  list_per_page = 25


admin.site.register(Mri, MriAdmin)



class XrayAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'xray_total')
  list_display_links = ('id', 'practice_manager', 'xray_total')
  list_filter = ('id', 'practice_manager', 'xray_total')
  search_fields = ('id', 'practice_manager', 'xray_total')
  list_per_page = 25


admin.site.register(Xray, XrayAdmin)




class CtscanAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'ctscan_total')
  list_display_links = ('id', 'practice_manager', 'ctscan_total')
  list_filter = ('id', 'practice_manager', 'ctscan_total')
  search_fields = ('id', 'practice_manager', 'ctscan_total')
  list_per_page = 25


admin.site.register(Ctscan, CtscanAdmin)

class FlouroscopyAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'flouroscopy_total')
  list_display_links = ('id', 'practice_manager', 'flouroscopy_total')
  list_filter = ('id', 'practice_manager', 'flouroscopy_total')
  search_fields = ('id', 'practice_manager', 'flouroscopy_total')
  list_per_page = 25


admin.site.register(Flouroscopy, FlouroscopyAdmin)



class MamographyAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'mamography_total')
  list_display_links = ('id', 'practice_manager', 'mamography_total')
  list_filter = ('id', 'practice_manager', 'mamography_total')
  search_fields = ('id', 'practice_manager', 'mamography_total')
  list_per_page = 25


admin.site.register(Mamography, MamographyAdmin)


class DentalxrayAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'dentalxray_total')
  list_display_links = ('id', 'practice_manager', 'dentalxray_total')
  list_filter = ('id', 'practice_manager', 'dentalxray_total')
  search_fields = ('id', 'practice_manager', 'dentalxray_total')
  list_per_page = 25


admin.site.register(Dentalxray, DentalxrayAdmin)


class AngiographyAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'angiography_total')
  list_display_links = ('id', 'practice_manager', 'angiography_total')
  list_filter = ('id', 'practice_manager', 'angiography_total')
  search_fields = ('id', 'practice_manager', 'angiography_total')
  list_per_page = 25


admin.site.register(Angiography, AngiographyAdmin)

class EchocardiographyAdmin(admin.ModelAdmin):
  list_display = ('id', 'practice_manager',  'echocardiography_total')
  list_display_links = ('id', 'practice_manager', 'echocardiography_total')
  list_filter = ('id', 'practice_manager', 'echocardiography_total')
  search_fields = ('id', 'practice_manager', 'echocardiography_total')
  list_per_page = 25


admin.site.register(Echocardiography, EchocardiographyAdmin)


class InspectionAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'license_category', 'address', 'inspection_date', 'inspection_total',)
  list_display_links = ('hospital_name', 'application_no', 'inspection_total')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'address', 'inspection_date', 'inspection_total',)
  list_per_page = 25


admin.site.register(Inspection, InspectionAdmin)

class AppraisalAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'license_category', 'address', 'inspection_date', 'appraisal_total',)
  list_display_links = ('hospital_name', 'application_no', 'appraisal_total')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'address', 'inspection_date', 'appraisal_total',)
  list_per_page = 25


admin.site.register(Appraisal, AppraisalAdmin)






class LicenseAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'address', 'license_category', 'issue_date', 'expiry_date',)
  list_display_links = ('application_no', 'hospital_name', 'license_category')
  list_filter = ('application_no',)
  search_fields = ('hospital_name', 'address', 'license_category', 'issue_date', 'expiry_date',)
  list_per_page = 25


admin.site.register(License, LicenseAdmin)


class RecordsAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'practice_category', 'address', 'state', 'equipment', 'date_visited',)
  list_display_links = ('hospital_name', 'practice_category')
  list_filter = ('hospital_name', 'address', 'equipment', 'date_visited', )
  search_fields = ('hospital_name', 'address', 'practice_category', 'radiographers', )
  list_per_page = 25


admin.site.register(Records, RecordsAdmin)




