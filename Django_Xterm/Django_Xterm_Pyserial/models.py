from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings

#Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields) 

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_professor = models.BooleanField(_('professor'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'is_professor']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def get_is_staff(self):
        '''
        Returns if the user is professor.
        '''
        return self.is_professor


class PowerStrip(models.Model):
    Name = models.CharField(max_length=50, null=False)
    Sockets = models.PositiveIntegerField(null=False)
    Has_wifi= models.BooleanField(default=False)
    Ip = models.CharField(max_length=50, null=True)
    Pin = models.CharField(max_length=50, null=True)
    Connected_In = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ('Name',)

    def __str__(self):
        return self.Name


class Status_Device(models.Model):
    DeviceName = models.CharField(max_length=50, null=False)
    Device = models.CharField(max_length=50, null=False)
    StatusDevice = models.CharField(max_length=50, null=True)
    PowerStrip = models.ForeignKey(PowerStrip, on_delete=models.SET_NULL, null=True)
    Socket = models.PositiveIntegerField(null=True)

    class Meta:
        ordering = ('Device',)

    def __str__(self):
        return self.Device


class Active_Device(models.Model):
    ActiveDevicesName = models.CharField(max_length=50)
    Created_time = models.DateTimeField(auto_now_add=True)
    User_using = models.EmailField()

    class Meta:
        ordering = ('ActiveDevicesName',)

    def __str__(self):
        return self.ActiveDevicesName


class Group(models.Model):
    Name = models.CharField(max_length=50, null=False)
    User = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    #Device = models.TextField(blank=True, null=False)

    class Meta:
        ordering = ('Name',)

    def __str__(self):
        return self.Name


class Group_NormalUser(models.Model):
    User = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    Group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ('Group',)


class Group_Device(models.Model):
    Status_Device = models.ForeignKey(Status_Device, on_delete=models.CASCADE, null=True)
    Group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ('Group',)
