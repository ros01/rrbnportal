from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _






class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        return self._create_user(email, password, **extra_fields)

    



class User(AbstractBaseUser, PermissionsMixin):

    ROLE = (
        ('Monitoring', 'Monitoring'),
        ('Zonal Offices', 'Zonal Offices'),
        ('Registrar', 'Registrar'),
        ('Finance', 'Finance'),
        )

    MODULE_NAME = (
        ('Monitoring HQ', 'Monitoring Hq'),
        ('Enugu Office', 'Enugu Office'),
        ('Lagos Office', 'Lagos Office'),
        ('Registrars Office', 'CEO'),
        ('Accounts HQ', 'FAH'),
        )


    HOSPITAL_TYPE = (
        ('Radiography Practice', 'Radiography Practice'),
        ('Radiography Internship', 'Radiography Internship'),
        )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_no = models.CharField(max_length=100, blank=True)
    hospital_name = models.CharField(max_length=200, blank=True)
    module_name = models.CharField (max_length=20, choices = MODULE_NAME, blank=True)
    role = models.CharField (max_length=30, choices = ROLE, blank=True)
    hospital_type = models.CharField (max_length=100, choices = HOSPITAL_TYPE, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    
    
    
    
    
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    
    
    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.email


    def reg_date_pretty(self):
        return self.date_joined .strftime('%b %e %Y')


    def get_absolute_url(self):
        return reverse("accounts:profile_detail", kwargs={"id": self.id})
   












   

