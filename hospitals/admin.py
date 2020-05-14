from django.contrib import admin

from .models import Registration, Payment, Inspection, License


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


class InspectionAdmin(admin.ModelAdmin):
  list_display = ('id', 'hospital_name', 'license_category', 'address', 'inspection_date', 'inspection_score')
  list_display_links = ('id', 'hospital_name')
  list_filter = ('hospital_name',)
  search_fields = ('hospital_name', 'address', 'inspection_date', 'inspection_score')
  list_per_page = 25


admin.site.register(Inspection, InspectionAdmin)



class LicenseAdmin(admin.ModelAdmin):
  list_display = ('id', 'hospital_name', 'address', 'license_category', 'license_no', 'issue_date', 'expiry_date', 'validity')
  list_display_links = ('id', 'hospital_name', 'license_category')
  list_filter = ('validity', 'license_no')
  search_fields = ('hospital_name', 'address', 'license_category', 'license_no', 'issue_date', 'expiry_date', 'status')
  list_per_page = 25


admin.site.register(License, LicenseAdmin)




