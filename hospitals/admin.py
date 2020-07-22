from django.contrib import admin

from .models import Registration, Payment, Inspection, License, Schedule, Records, Appraisal


class RegistrationAdmin(admin.ModelAdmin):
  list_display = ('application_no', 'hospital_name', 'license_category', 'address', 'state',
                  'services', 'equipment', 'radiographers')
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




