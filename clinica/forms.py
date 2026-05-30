from django import forms
from django.contrib.auth.models import User

from .models import Tutor, Paciente, Consulta, PerfilUsuario


class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['nombre', 'rut', 'telefono', 'email', 'direccion', 'ciudad', 'contacto_emergencia', 'observaciones']


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'especie', 'raza', 'sexo', 'fecha_nacimiento', 'peso', 'color', 'microchip', 'alergias', 'observaciones', 'tutor']


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            'paciente', 'veterinario', 'fecha', 'hora', 'motivo',
            'peso_visita', 'temperatura', 'diagnostico', 'tratamiento',
            'requiere_seguimiento', 'fecha_proxima_visita', 'indicaciones_tutor',
        ]


class ConsultaEditForm(forms.ModelForm):
    """Formulario completo para editar una consulta existente."""
    class Meta:
        model = Consulta
        fields = [
            'veterinario', 'fecha', 'hora', 'motivo', 'estado',
            'peso_visita', 'temperatura', 'diagnostico', 'tratamiento',
            'requiere_seguimiento', 'fecha_proxima_visita', 'indicaciones_tutor',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'fecha_proxima_visita': forms.DateInput(attrs={'type': 'date'}),
            'diagnostico': forms.Textarea(attrs={'rows': 4}),
            'tratamiento': forms.Textarea(attrs={'rows': 4}),
            'indicaciones_tutor': forms.Textarea(attrs={'rows': 3}),
        }


class CrearUsuarioForm(forms.Form):
    nombre = forms.CharField(max_length=150, label='Nombre')
    apellido = forms.CharField(max_length=150, label='Apellido')
    email = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña', min_length=8)
    rol = forms.ChoiceField(choices=[], label='Rol')

    def __init__(self, *args, roles_permitidos=None, **kwargs):
        super().__init__(*args, **kwargs)
        etiquetas = dict(PerfilUsuario.ROL)
        self.fields['rol'].choices = [
            (r, etiquetas.get(r, r)) for r in (roles_permitidos or [])
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con ese correo.')
        return email
