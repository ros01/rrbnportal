from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User, Hospital
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms


class AddUserForm(forms.ModelForm):
    """
    New User Form. Requires password confirmation.
    """
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirm password', widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'module_name', 'role', 'license_type')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UpdateUserForm(forms.ModelForm):
    """
    Update User Form. Doesn't allow changing password in the Admin.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'is_active',
                  'is_staff', 'module_name', 'role', 'license_type'  
        )

    def clean_password(self):
        # Password can't be changed in the admin
        return self.initial["password"]




class UserAdmin(BaseUserAdmin):
    form = UpdateUserForm
    add_form = AddUserForm

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('email', 'is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
        ('Profiles', {'fields': ('module_name', 'role', 'license_type')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email', 'first_name', 'last_name', 'password1',
                    'password2'
                )
            }
        ),
    )
    search_fields = ('email', 'first_name', 'last_name', 'role')
    ordering = ('email', 'first_name', 'last_name')
    filter_horizontal = ()
    list_per_page = 25


admin.site.register(User, UserAdmin)




class HospitalAdmin(admin.ModelAdmin):
  list_display = ('hospital_name', 'rc_number', 'phone_no', 'reg_date')
  list_display_links = ('hospital_name', 'rc_number' )
  list_filter = ('hospital_name', 'rc_number' )
  search_fields = ('hospital_name', 'rc_number')
  list_per_page = 25


admin.site.register(Hospital, HospitalAdmin)
