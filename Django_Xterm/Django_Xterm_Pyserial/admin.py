from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from . import models

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

admin.site.unregister(Group)

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.User
        fields = ('email', 'is_professor')

    def clean_password2(self):
        # Compruebe que las dos entradas de contraseña coincidan
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Guarde la contraseña proporcionada en formato hash
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=('Password'),
                help_text=("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"../password/\">this form</a>."))

    class Meta:
        model = models.User
        fields = ('email', 'password', 'is_active', 'is_staff', 'is_professor')

    # Guardar la contraseña al meter el resto de datos.
    def clean_password(self):
        return self.initial['password']


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    # Los formularios para agregar y cambiar instancias de usuario
    form = UserChangeForm
    add_form = UserCreationForm

    # Los campos que se utilizarán para mostrar el modelo de usuario.
    # Estos anulan las definiciones en el UserAdmin base
    # que hacen referencia a campos específicos en auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_professor', 'password')
    list_filter = ('is_professor', 'is_staff', )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', )}),
        ('Permissions', {'fields': ('is_staff', 'is_professor',)}),
    )
    # add_fieldsets no es un atributo ModelAdmin estándar. UserAdmin
    # anula get_fieldsets para usar este atributo al crear un usuario.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_professor', ),
        }),
    )
    search_fields = ('email', 'last_name', )
    ordering = ('last_name',)
    filter_horizontal = ()


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('Name','User')

    search_fields = ("Name", )


@admin.register(models.Group_NormalUser)
class Group_NormalUserAdmin(admin.ModelAdmin):
    list_display = ('User','Group')

    search_fields = ("Group", 'User', )


@admin.register(models.Active_Device)
class Active_DeviceAdmin(admin.ModelAdmin):
    list_display = ('ActiveDevicesName','Created_time', 'User_using')

    search_fields = ("ActiveDevicesName", )


@admin.register(models.Status_Device)
class Status_DeviceAdmin(admin.ModelAdmin):
    list_display = ('DeviceName','Device','StatusDevice','PowerStrip', 'Socket')
    actions = None

    search_fields = ("Device", "DeviceName", )

@admin.register(models.PowerStrip)
class PowerStripAdmin(admin.ModelAdmin):
    list_display = ('Name','Sockets','Has_wifi','Ip','Pin','Connected_In')

    search_fields = ("Name", )

@admin.register(models.Group_Device)
class Group_DeviceAdmin(admin.ModelAdmin):
    list_display = ('Status_Device','Group')

    search_fields = ("Group", 'Status_Device', )
