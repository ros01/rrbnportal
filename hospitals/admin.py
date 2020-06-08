from django.contrib import admin

from .models import Registration, Payment, Inspection, License, Schedule


class RegistrationAdmin(admin.ModelAdmin):
  list_display = ('id', 'hospital_name', 'license_category', 'address', 'state',
                  'services', 'equipment', 'radiographers')
  list_display_links = ('id', 'hospital_name')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'address', 'state',
                   'services', 'equipment', 'radiographers')
  list_per_page = 25


admin.site.register(Registration, RegistrationAdmin)

class PaymentAdmin(admin.ModelAdmin):
  list_display = ('id', 'hospital_name', 'license_category', 'rrr_number', 'receipt_number', 'payment_amount',
                  'payment_receipt', 'payment_date')
  list_display_links = ('id', 'hospital_name')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'receipt_number', 'payment_date',
                  'payment_date')
  list_per_page = 25


admin.site.register(Payment, PaymentAdmin)



class ScheduleAdmin(admin.ModelAdmin):
  list_display = ('id', 'application_no', 'hospital_name',  'address', 'equipment',
   'inspection_date', 'inspection_report_deadline', 'inspection_zone',)
  list_display_links = ('id', 'application_no', 'hospital_name', 'inspection_date', 'inspection_zone',)
  list_filter = ('application_no', 'hospital_name', 'inspection_date', 'inspection_zone',)
  search_fields = ('hospital_name', 'application_no','equipment', 'inspection_date', 'inspection_zone',)
  list_per_page = 25


admin.site.register(Schedule, ScheduleAdmin)


class InspectionAdmin(admin.ModelAdmin):
  list_display = ('id', 'application_no', 'hospital_name', 'license_category', 'address', 'inspection_date', 'inspection_scores')
  list_display_links = ('id', 'hospital_name', 'application_no')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'address', 'inspection_date', 'inspection_scores')
  list_per_page = 25


admin.site.register(Inspection, InspectionAdmin)






class LicenseAdmin(admin.ModelAdmin):
  list_display = ('id', 'hospital_name', 'address', 'license_category', 'issue_date', 'expiry_date',)
  list_display_links = ('id', 'hospital_name', 'license_category')
  list_filter = ('id',)
  search_fields = ('hospital_name', 'address', 'license_category', 'issue_date', 'expiry_date',)
  list_per_page = 25


admin.site.register(License, LicenseAdmin)




