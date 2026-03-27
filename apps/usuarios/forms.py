from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class CrearUsuarioForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'cedula', 'foto', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electronico',
            'cedula': 'Cedula',
            'foto': 'Foto del candidato',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos.'
        self.fields['password1'].help_text = (
            'La contraseña debe tener al menos 8 caracteres y no ser comun.'
        )
        self.fields['password2'].help_text = 'Ingresa la misma contraseña para confirmarla.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'CANDIDATO'
        if commit:
            user.save()
        return user


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'cedula', 'foto']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electronico',
            'cedula': 'Cedula',
            'foto': 'Foto del candidato',
        }
