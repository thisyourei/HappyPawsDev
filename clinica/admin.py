from django.contrib import admin
from .models import Tutor, Paciente, Veterinario, Consulta, Patologia, Vacuna


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'ciudad']
    search_fields = ['nombre', 'email', 'rut']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especie', 'raza', 'sexo', 'estado', 'tutor']
    list_filter = ['especie', 'sexo', 'estado']
    search_fields = ['nombre', 'microchip', 'raza']


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ['nombre']


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'veterinario', 'fecha', 'hora', 'motivo', 'estado']
    list_filter = ['estado', 'fecha', 'veterinario']
    search_fields = ['paciente__nombre', 'motivo']
    date_hierarchy = 'fecha'


@admin.register(Patologia)
class PatologiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'paciente', 'tipo', 'fecha_diagnostico']
    list_filter = ['tipo']
    search_fields = ['nombre', 'paciente__nombre']


@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'paciente', 'fecha_aplicacion', 'proxima_dosis']
    search_fields = ['nombre', 'paciente__nombre']
