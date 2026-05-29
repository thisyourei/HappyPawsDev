from django import forms
from .models import Mascota, Tutor, Veterinario, Informe

class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['nombre', 'correo', 'telefono', 'direccion']

class VeterinarioForm(forms.ModelForm):
    class Meta:
        model = Veterinario
        fields = ['nombre', 'especialidad', 'correo', 'telefono']

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'sexo', 'edad_meses', 'peso', 'tutor', 'veterinario']

class InformeForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Informe
        fields = ['mascota', 'veterinario', 'tipo', 'titulo', 'descripcion', 'resultado', 'fecha']
