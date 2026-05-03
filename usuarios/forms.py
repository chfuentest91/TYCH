from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
import re

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'rut',
                  'fecha_nacimiento', 'direccion', 'telefono', 'foto_perfil']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['rut'].label = 'RUT'
        self.fields['fecha_nacimiento'].label = 'Fecha de Nacimiento'
        self.fields['direccion'].label = 'Dirección'
        self.fields['telefono'].label = 'Teléfono'
        self.fields['foto_perfil'].label = 'Foto de perfil'
        self.fields['foto_perfil'].required = False

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name != 'foto_perfil':
                field.required = True

        self.fields['fecha_nacimiento'].widget = forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
        self.fields['rut'].widget.attrs['placeholder'] = 'Ej: 12.345.678-9'
        self.fields['telefono'].widget.attrs['placeholder'] = 'Ej: +56912345678'
        self.fields['direccion'].widget.attrs['placeholder'] = 'Ej: Av. Providencia 123, Santiago'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '')
        patron = r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$'
        if not re.match(patron, rut):
            raise forms.ValidationError(
                'Formato de RUT inválido. Use el formato: 12.345.678-9'
            )
        return rut

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        patron = r'^\+?[0-9]{9,12}$'
        if not re.match(patron, telefono):
            raise forms.ValidationError(
                'Teléfono inválido. Use el formato: +56912345678'
            )
        return telefono