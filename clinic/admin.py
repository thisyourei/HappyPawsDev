from django.contrib import admin
from .models import Mascota, Tutor, Veterinario, Informe

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo', 'creado')
    search_fields = ('nombre', 'correo')

@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad', 'telefono', 'correo', 'creado')
    search_fields = ('nombre', 'especialidad')

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'tutor', 'veterinario', 'creado')
    list_filter = ('especie', 'sexo')
    search_fields = ('nombre', 'raza', 'tutor__nombre')

@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'mascota', 'tipo', 'fecha', 'veterinario')
    list_filter = ('tipo', 'fecha')
    search_fields = ('titulo', 'mascota__nombre', 'veterinario__nombre')
