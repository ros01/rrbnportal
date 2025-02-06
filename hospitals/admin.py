from django.contrib import admin

from .models import *


class DocumentAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'application_type', 'license_type', 'hospital_name', 'hospital_type', 'equipment', 'date')
  list_display_links = ('application_no', 'application_type', 'license_type', 'date')
  list_filter = ('hospital_name', 'date')
  search_fields = ('hospital_name__hospital_name', 'application_no', 'application_type', 'license_type', 'hospital_type', 'equipment', 'date')
  list_per_page = 25


admin.site.register(Document, DocumentAdmin)

class InspectorAdmin(admin.ModelAdmin):
  list_display = ('name', 'phone_number', 'zone', 'is_approved')
  list_display_links = ('name', 'phone_number')
  list_filter = ('name', 'phone_number')
  search_fields = ('name', 'phone_number')
  list_per_page = 25


admin.site.register(Inspector, InspectorAdmin)


class PaymentAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name','rrr_number', 'payment_amount', 'payment_receipt', 'vet_status', 'payment_date')
  list_display_links = ('application_no', 'hospital_name')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'receipt_number', 'payment_date',
                  'payment_date')
  list_per_page = 25


admin.site.register(Payment, PaymentAdmin)



class ScheduleAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'inspection_schedule_date', 'inspection_date', 'inspection_report_deadline', 'inspection_zone',)
  list_display_links = ('application_no', 'hospital_name', 'inspection_date', 'inspection_zone',)
  list_filter = ('application_no', 'hospital_name', 'inspection_date', 'inspection_zone',)
  #fieldsets = (
        #(None, {'fields': ('application_no', 'hospital_name', 'inspection_date', 'inspection_report_deadline', 'inspection_zone',)}),
        #('Inspection Scores', {'fields': ('nuclear_medicine_total', 'carm_total', 'radiotherapy_total', 'mri_total', 'ultrasound_total', 'ctscan_total', 'xray_total', 'flouroscopy_total',  'mamography_total', 'echocardiography_total', 'dentalxray_total', 'angiography_total',)}),
    #)
  search_fields = ('hospital_name', 'application_no', 'inspection_date', 'inspection_zone',)
  list_per_page = 25

admin.site.register(Schedule, ScheduleAdmin)

class NuclearmedicineAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'nuclear_medicine_total')
  list_display_links = ('hospital_name', 'application_no', 'nuclear_medicine_total')
  list_filter = ('hospital_name', 'application_no', 'nuclear_medicine_total')
  search_fields = ('hospital_name', 'application_no', 'nuclear_medicine_total')
  list_per_page = 25


admin.site.register(Nuclearmedicine, NuclearmedicineAdmin)

class RadiotherapyAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'radiotherapy_total')
  list_display_links = ('hospital_name', 'application_no', 'radiotherapy_total')
  list_filter = ('hospital_name', 'application_no', 'radiotherapy_total')
  search_fields = ('hospital_name', 'application_no', 'radiotherapy_total')
  list_per_page = 25


admin.site.register(Radiotherapy, RadiotherapyAdmin)



class UltrasoundAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'ultrasound_total')
  list_display_links = ('hospital_name', 'application_no', 'ultrasound_total')
  list_filter = ('hospital_name', 'application_no', 'ultrasound_total')
  search_fields = ('hospital_name','application_no', 'ultrasound_total')
  list_per_page = 25


admin.site.register(Ultrasound, UltrasoundAdmin)


class MriAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'mri_total')
  list_display_links = ('hospital_name', 'application_no', 'mri_total')
  list_filter = ('hospital_name', 'application_no', 'mri_total')
  search_fields = ('hospital_name', 'application_no', 'mri_total')
  list_per_page = 25


admin.site.register(Mri, MriAdmin)



class XrayAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'xray_total')
  list_display_links = ('hospital_name', 'application_no', 'xray_total')
  list_filter = ('hospital_name', 'application_no', 'xray_total')
  search_fields = ('hospital_name', 'application_no', 'xray_total')
  list_per_page = 25


admin.site.register(Xray, XrayAdmin)




class CtscanAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'ctscan_total')
  list_display_links = ('hospital_name', 'application_no', 'ctscan_total')
  list_filter = ('hospital_name', 'application_no', 'ctscan_total')
  search_fields = ('hospital_name', 'application_no', 'ctscan_total')
  list_per_page = 25


admin.site.register(Ctscan, CtscanAdmin)

class FlouroscopyAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'flouroscopy_total')
  list_display_links = ('hospital_name', 'application_no', 'flouroscopy_total')
  list_filter = ('hospital_name', 'application_no', 'flouroscopy_total')
  search_fields = ('hospital_name', 'application_no', 'flouroscopy_total')
  list_per_page = 25


admin.site.register(Flouroscopy, FlouroscopyAdmin)



class MamographyAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'mamography_total')
  list_display_links = ('hospital_name', 'application_no', 'mamography_total')
  list_filter = ('hospital_name', 'application_no', 'mamography_total')
  search_fields = ('hospital_name', 'application_no', 'mamography_total')
  list_per_page = 25


admin.site.register(Mamography, MamographyAdmin)


class DentalxrayAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'dentalxray_total')
  list_display_links = ('hospital_name', 'application_no', 'dentalxray_total')
  list_filter = ('hospital_name', 'application_no', 'dentalxray_total')
  search_fields = ('hospital_name', 'application_no', 'dentalxray_total')
  list_per_page = 25


admin.site.register(Dentalxray, DentalxrayAdmin)


class AngiographyAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'angiography_total')
  list_display_links = ('hospital_name', 'application_no', 'angiography_total')
  list_filter = ('hospital_name', 'application_no', 'angiography_total')
  search_fields = ('hospital_name', 'application_no', 'angiography_total')
  list_per_page = 25


admin.site.register(Angiography, AngiographyAdmin)

class EchocardiographyAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'echocardiography_total')
  list_display_links = ('hospital_name', 'application_no', 'echocardiography_total')
  list_filter = ('hospital_name', 'application_no', 'echocardiography_total')
  search_fields = ('hospital_name', 'application_no', 'echocardiography_total')
  list_per_page = 25


admin.site.register(Echocardiography, EchocardiographyAdmin)


class CarmAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'application_no', 'carm_total')
  list_display_links = ('hospital_name', 'application_no', 'carm_total')
  list_filter = ('hospital_name', 'application_no', 'carm_total')
  search_fields = ('hospital_name', 'application_no', 'carm_total')
  list_per_page = 25


admin.site.register(Carm, CarmAdmin)


class InspectionAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'inspection_total', 'inspection_date',)
  list_display_links = ('hospital_name', 'application_no', 'inspection_total')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'inspection_total',)
  list_per_page = 25


admin.site.register(Inspection, InspectionAdmin)

class AppraisalAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'appraisal_total', 'appraisal_date',)
  list_display_links = ('hospital_name', 'application_no', 'appraisal_total')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'appraisal_total',)
  list_per_page = 25


admin.site.register(Appraisal, AppraisalAdmin)






class LicenseAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'issue_date', 'expiry_date',)
  list_display_links = ('application_no', 'hospital_name')
  list_filter = ('application_no',)
  search_fields = ('hospital_name', 'issue_date', 'expiry_date',)
  list_per_page = 25


admin.site.register(License, LicenseAdmin)


class RecordsAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'practice_category', 'address', 'state', 'equipment', 'date_visited',)
  list_display_links = ('hospital_name', 'practice_category')
  list_filter = ('hospital_name', 'address', 'equipment', 'date_visited', )
  search_fields = ('hospital_name', 'address', 'practice_category', 'radiographers', )
  list_per_page = 25


admin.site.register(Records, RecordsAdmin)




