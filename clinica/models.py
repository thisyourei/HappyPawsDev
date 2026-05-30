from django.contrib.auth.models import User
from django.db import models


class PerfilUsuario(models.Model):
    ROL = [
        ('administrador', 'Administrador'),
        ('veterinario', 'Veterinario'),
        ('recepcionista', 'Recepcionista'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROL)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.get_rol_display()})'

    @property
    def nombre_completo(self):
        return self.user.get_full_name() or self.user.username

    @property
    def puede_registrar(self):
        """Puede crear nuevos pacientes y tutores"""
        return self.rol in ('administrador', 'veterinario')

    @property
    def puede_gestionar_usuarios(self):
        """Puede ver y crear usuarios"""
        return self.rol in ('administrador', 'veterinario')

    @property
    def puede_crear_veterinarios(self):
        """Solo el administrador puede crear cuentas de veterinario"""
        return self.rol == 'administrador'

    @property
    def roles_que_puede_crear(self):
        if self.rol == 'administrador':
            return ['veterinario', 'recepcionista']
        if self.rol == 'veterinario':
            return ['recepcionista']
        return []

    class Meta:
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuarios'


class Tutor(models.Model):
    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    contacto_emergencia = models.CharField(max_length=20, blank=True)
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = 'tutores'
        ordering = ['nombre']


class Paciente(models.Model):
    ESPECIE = [
        ('canino', 'Canino'),
        ('felino', 'Felino'),
        ('ave', 'Ave'),
        ('reptil', 'Reptil'),
        ('roedor', 'Roedor'),
        ('otro', 'Otro'),
    ]
    SEXO = [
        ('M', 'Macho'),
        ('F', 'Hembra'),
    ]
    ESTADO = [
        ('activo', 'Activo'),
        ('seguimiento', 'Seguimiento'),
        ('urgente', 'Urgente'),
        ('inactivo', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=200)
    especie = models.CharField(max_length=20, choices=ESPECIE)
    raza = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=100, blank=True)
    microchip = models.CharField(max_length=20, blank=True)
    alergias = models.CharField(max_length=500, blank=True)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='activo')
    tutor = models.ForeignKey(Tutor, on_delete=models.PROTECT, related_name='pacientes')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} ({self.get_especie_display()})'

    class Meta:
        ordering = ['-creado']


class Veterinario(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = 'veterinarios'
        ordering = ['nombre']


class Consulta(models.Model):
    SEGUIMIENTO = [
        ('no', 'No'),
        ('programada', 'Sí — próxima cita programada'),
        ('urgente', 'Sí — urgente'),
    ]
    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('completada', 'Completada'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT, related_name='consultas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=300)
    peso_visita = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    diagnostico = models.TextField(blank=True)
    tratamiento = models.TextField(blank=True)
    requiere_seguimiento = models.CharField(max_length=20, choices=SEGUIMIENTO, default='no')
    fecha_proxima_visita = models.DateField(null=True, blank=True)
    indicaciones_tutor = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.paciente} — {self.fecha} {self.hora}'

    class Meta:
        ordering = ['-fecha', '-hora']


class Patologia(models.Model):
    TIPO = [
        ('cronica', 'Crónica'),
        ('aguda', 'Aguda'),
        ('alerta', 'Alerta'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='patologias')
    nombre = models.CharField(max_length=200)
    fecha_diagnostico = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO)
    tratamiento_actual = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f'{self.nombre} — {self.paciente}'

    class Meta:
        verbose_name_plural = 'patologías'
        ordering = ['-fecha_diagnostico']


class Vacuna(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='vacunas')
    nombre = models.CharField(max_length=200)
    fecha_aplicacion = models.DateField()
    proxima_dosis = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.nombre} — {self.paciente}'

    class Meta:
        verbose_name_plural = 'vacunas'
        ordering = ['-fecha_aplicacion']
