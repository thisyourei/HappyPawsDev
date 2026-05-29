from django.db import models

class Tutor(models.Model):
    nombre = models.CharField(max_length=140)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=260, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'

    def __str__(self):
        return self.nombre

class Veterinario(models.Model):
    nombre = models.CharField(max_length=140)
    especialidad = models.CharField(max_length=120, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Veterinario'
        verbose_name_plural = 'Veterinarios'

    def __str__(self):
        return self.nombre

class Mascota(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Hembra'),
    ]
    nombre = models.CharField(max_length=120)
    especie = models.CharField(max_length=80)
    raza = models.CharField(max_length=120, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='M')
    edad_meses = models.PositiveIntegerField(default=0)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='mascotas')
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, blank=True, null=True, related_name='pacientes')
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'

    def __str__(self):
        return f'{self.nombre} ({self.especie})'

class Informe(models.Model):
    TIPO_CHOICES = [
        ('consulta', 'Consulta'),
        ('examen', 'Examen'),
        ('diagnostico', 'Diagnóstico'),
    ]
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='informes')
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True)
    resultado = models.TextField(blank=True)
    fecha = models.DateField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Informe'
        verbose_name_plural = 'Informes'
        ordering = ['-fecha', '-creado']

    def __str__(self):
        return f'{self.titulo} - {self.mascota.nombre}'
