from django import forms
from .models import Tutor, Paciente, Consulta


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
