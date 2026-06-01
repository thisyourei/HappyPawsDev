import random
from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from clinica.models import (
    Consulta,
    Paciente,
    Patologia,
    PerfilUsuario,
    Tutor,
    Vacuna,
    Veterinario,
)


class Command(BaseCommand):
    help = 'Carga datos de prueba: tutores, mascotas, veterinarios y consultas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos existentes antes de insertar',
        )
        parser.add_argument(
            '--factor',
            type=int,
            default=1,
            help='Multiplicador de volumen de datos masivos (ej. 20)',
        )
        parser.add_argument(
            '--consultas',
            type=int,
            default=0,
            help='Total objetivo de consultas (rellena con fechas ene-2026 → hoy)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando datos existentes...')
            Consulta.objects.all().delete()
            Vacuna.objects.all().delete()
            Patologia.objects.all().delete()
            Paciente.objects.all().delete()
            Tutor.objects.all().delete()
            Veterinario.objects.all().delete()
            self.stdout.write(self.style.WARNING('Datos eliminados.'))

        self._crear_usuarios()
        vets = self._crear_veterinarios()
        tutores = self._crear_tutores()
        pacientes = self._crear_pacientes(tutores)
        self._crear_vacunas(pacientes)
        self._crear_patologias(pacientes)
        self._crear_consultas(pacientes, vets)

        factor = options.get('factor', 1)
        if factor and factor > 1:
            self._crear_masivos(factor, vets)

        objetivo_consultas = options.get('consultas', 0)
        if objetivo_consultas and objetivo_consultas > 0:
            self._crear_consultas_masivas(objetivo_consultas, vets)

        self.stdout.write(self.style.SUCCESS('\n✔ Datos de prueba cargados exitosamente.'))
        self.stdout.write(
            f'  Totales — Tutores: {Tutor.objects.count()} · '
            f'Pacientes: {Paciente.objects.count()} · '
            f'Consultas: {Consulta.objects.count()} · '
            f'Vacunas: {Vacuna.objects.count()}'
        )
        self.stdout.write('  Usuario admin: admin / admin1234')
        self.stdout.write('  Usuario veterinario: dr.silva / vet1234')
        self.stdout.write('  Usuario recepcion: recepcion / recep1234')

    # ------------------------------------------------------------------
    def _crear_usuarios(self):
        self.stdout.write('Creando usuarios...')

        if not User.objects.filter(username='admin').exists():
            u = User.objects.create_superuser('admin', 'admin@happypaws.cl', 'admin1234')
            u.first_name = 'Admin'
            u.last_name = 'HappyPaws'
            u.save()
            PerfilUsuario.objects.get_or_create(user=u, defaults={'rol': 'administrador'})

        if not User.objects.filter(username='dr.silva').exists():
            u = User.objects.create_user('dr.silva', 'silva@happypaws.cl', 'vet1234',
                                         first_name='Carlos', last_name='Silva')
            PerfilUsuario.objects.get_or_create(user=u, defaults={'rol': 'veterinario'})

        if not User.objects.filter(username='recepcion').exists():
            u = User.objects.create_user('recepcion', 'recepcion@happypaws.cl', 'recep1234',
                                         first_name='María', last_name='González')
            PerfilUsuario.objects.get_or_create(user=u, defaults={'rol': 'recepcionista'})

    # ------------------------------------------------------------------
    def _crear_veterinarios(self):
        self.stdout.write('Creando veterinarios...')
        datos = [
            'Dr. Carlos Silva',
            'Dra. Ana Martínez',
            'Dr. Felipe Rojas',
        ]
        vets = []
        for nombre in datos:
            v, _ = Veterinario.objects.get_or_create(nombre=nombre)
            vets.append(v)
        return vets

    # ------------------------------------------------------------------
    def _crear_tutores(self):
        self.stdout.write('Creando tutores...')
        datos = [
            {
                'nombre': 'Valentina Torres',
                'rut': '15.234.567-8',
                'telefono': '+56 9 8123 4567',
                'email': 'valentina.torres@gmail.com',
                'direccion': 'Av. Providencia 1234, Dpto 5B',
                'ciudad': 'Santiago',
                'contacto_emergencia': '+56 9 9876 5432',
                'observaciones': 'Prefiere contacto por WhatsApp.',
            },
            {
                'nombre': 'Rodrigo Fuentes',
                'rut': '12.345.678-9',
                'telefono': '+56 9 7654 3210',
                'email': 'rodrigo.fuentes@outlook.com',
                'direccion': 'Calle Los Pinos 456',
                'ciudad': 'Las Condes',
                'contacto_emergencia': '+56 9 6543 2109',
                'observaciones': '',
            },
            {
                'nombre': 'Camila Herrera',
                'rut': '17.890.123-4',
                'telefono': '+56 9 5432 1098',
                'email': 'camila.herrera@gmail.com',
                'direccion': 'Pasaje El Roble 78',
                'ciudad': 'Ñuñoa',
                'contacto_emergencia': '+56 9 4321 0987',
                'observaciones': 'Trabaja hasta las 18:00, llamar antes.',
            },
            {
                'nombre': 'Sebastián Morales',
                'rut': '14.567.890-2',
                'telefono': '+56 9 3210 9876',
                'email': 'sebastian.morales@empresa.cl',
                'direccion': 'Av. Kennedy 2345, Of. 302',
                'ciudad': 'Vitacura',
                'contacto_emergencia': '+56 9 2109 8765',
                'observaciones': 'Tiene dos mascotas registradas.',
            },
            {
                'nombre': 'Isabel Díaz',
                'rut': '16.123.456-7',
                'telefono': '+56 9 1098 7654',
                'email': 'isabel.diaz@hotmail.com',
                'direccion': 'Los Aromos 321',
                'ciudad': 'Maipú',
                'contacto_emergencia': '+56 9 0987 6543',
                'observaciones': '',
            },
        ]
        tutores = []
        for d in datos:
            t, _ = Tutor.objects.get_or_create(rut=d['rut'], defaults=d)
            tutores.append(t)
        return tutores

    # ------------------------------------------------------------------
    def _crear_pacientes(self, tutores):
        self.stdout.write('Creando pacientes (mascotas)...')
        hoy = date.today()
        datos = [
            {
                'nombre': 'Luna',
                'especie': 'canino',
                'raza': 'Golden Retriever',
                'sexo': 'F',
                'fecha_nacimiento': hoy - timedelta(days=365 * 3),
                'peso': 28.50,
                'color': 'Dorado',
                'microchip': 'MC001234567',
                'alergias': '',
                'observaciones': 'Muy sociable, no agresiva.',
                'estado': 'activo',
                'tutor': tutores[0],
            },
            {
                'nombre': 'Max',
                'especie': 'canino',
                'raza': 'Labrador Negro',
                'sexo': 'M',
                'fecha_nacimiento': hoy - timedelta(days=365 * 5),
                'peso': 34.00,
                'color': 'Negro',
                'microchip': 'MC002345678',
                'alergias': 'Pollo (dieta especial)',
                'observaciones': 'Alérgico al pollo. Dieta de cordero.',
                'estado': 'seguimiento',
                'tutor': tutores[1],
            },
            {
                'nombre': 'Michi',
                'especie': 'felino',
                'raza': 'Siamés',
                'sexo': 'M',
                'fecha_nacimiento': hoy - timedelta(days=365 * 2),
                'peso': 4.20,
                'color': 'Crema con puntas oscuras',
                'microchip': '',
                'alergias': '',
                'observaciones': 'Gato de interior.',
                'estado': 'activo',
                'tutor': tutores[2],
            },
            {
                'nombre': 'Copito',
                'especie': 'canino',
                'raza': 'Bichón Frisé',
                'sexo': 'M',
                'fecha_nacimiento': hoy - timedelta(days=365 * 1),
                'peso': 5.80,
                'color': 'Blanco',
                'microchip': 'MC003456789',
                'alergias': '',
                'observaciones': 'Cachorro activo.',
                'estado': 'activo',
                'tutor': tutores[3],
            },
            {
                'nombre': 'Pelusa',
                'especie': 'felino',
                'raza': 'Angora',
                'sexo': 'F',
                'fecha_nacimiento': hoy - timedelta(days=365 * 4),
                'peso': 3.90,
                'color': 'Blanco',
                'microchip': '',
                'alergias': '',
                'observaciones': '',
                'estado': 'activo',
                'tutor': tutores[3],
            },
            {
                'nombre': 'Rocko',
                'especie': 'canino',
                'raza': 'Pastor Alemán',
                'sexo': 'M',
                'fecha_nacimiento': hoy - timedelta(days=365 * 7),
                'peso': 38.00,
                'color': 'Negro y café',
                'microchip': 'MC004567890',
                'alergias': '',
                'observaciones': 'Displasia de cadera diagnosticada.',
                'estado': 'seguimiento',
                'tutor': tutores[4],
            },
            {
                'nombre': 'Tweety',
                'especie': 'ave',
                'raza': 'Canario',
                'sexo': 'M',
                'fecha_nacimiento': hoy - timedelta(days=365 * 2),
                'peso': 0.03,
                'color': 'Amarillo',
                'microchip': '',
                'alergias': '',
                'observaciones': 'Ave de interior. Muy activo.',
                'estado': 'activo',
                'tutor': tutores[0],
            },
            {
                'nombre': 'Rex',
                'especie': 'canino',
                'raza': 'Mestizo',
                'sexo': 'M',
                'fecha_nacimiento': hoy - timedelta(days=365 * 6),
                'peso': 22.00,
                'color': 'Café moteado',
                'microchip': '',
                'alergias': '',
                'observaciones': 'Rescatado de la calle. Completamente vacunado.',
                'estado': 'urgente',
                'tutor': tutores[2],
            },
        ]
        pacientes = []
        for d in datos:
            p, _ = Paciente.objects.get_or_create(
                nombre=d['nombre'],
                tutor=d['tutor'],
                defaults=d,
            )
            pacientes.append(p)
        return pacientes

    # ------------------------------------------------------------------
    def _crear_vacunas(self, pacientes):
        self.stdout.write('Creando vacunas...')
        hoy = date.today()
        vacunas_caninos = [
            ('Sextuple', -365, 365),
            ('Antirrábica', -180, 180),
            ('Bordetella', -90, 270),
        ]
        vacunas_felinos = [
            ('Triple Felina', -365, 365),
            ('Antirrábica Felina', -200, 165),
        ]
        for p in pacientes:
            if p.especie == 'canino':
                lista = vacunas_caninos
            elif p.especie == 'felino':
                lista = vacunas_felinos
            else:
                continue
            for nombre, dias_app, dias_prox in lista:
                Vacuna.objects.get_or_create(
                    paciente=p,
                    nombre=nombre,
                    defaults={
                        'fecha_aplicacion': hoy + timedelta(days=dias_app),
                        'proxima_dosis': hoy + timedelta(days=dias_prox),
                    },
                )

    # ------------------------------------------------------------------
    def _crear_patologias(self, pacientes):
        self.stdout.write('Creando patologías...')
        hoy = date.today()

        def agregar(paciente_nombre, patologias):
            for p in pacientes:
                if p.nombre == paciente_nombre:
                    for pat in patologias:
                        Patologia.objects.get_or_create(
                            paciente=p,
                            nombre=pat['nombre'],
                            defaults=pat,
                        )

        agregar('Max', [
            {
                'nombre': 'Alergia alimentaria (pollo)',
                'fecha_diagnostico': hoy - timedelta(days=300),
                'tipo': 'cronica',
                'tratamiento_actual': 'Dieta hipoalergénica de cordero',
                'observaciones': 'Confirmar con propietario antes de cada consulta.',
            }
        ])
        agregar('Rocko', [
            {
                'nombre': 'Displasia de cadera bilateral',
                'fecha_diagnostico': hoy - timedelta(days=200),
                'tipo': 'cronica',
                'tratamiento_actual': 'Meloxicam 0.1 mg/kg c/24h, fisioterapia semanal',
                'observaciones': 'Control radiológico cada 6 meses.',
            }
        ])
        agregar('Rex', [
            {
                'nombre': 'Dermatitis crónica',
                'fecha_diagnostico': hoy - timedelta(days=45),
                'tipo': 'alerta',
                'tratamiento_actual': 'Shampoo medicado, Omega-3',
                'observaciones': 'Revisar en próxima visita.',
            }
        ])

    # ------------------------------------------------------------------
    def _crear_consultas(self, pacientes, vets):
        self.stdout.write('Creando consultas...')
        hoy = date.today()

        def pac(nombre):
            return next((p for p in pacientes if p.nombre == nombre), pacientes[0])

        consultas = [
            # Consultas completadas (pasado)
            {
                'paciente': pac('Luna'),
                'veterinario': vets[0],
                'fecha': hoy - timedelta(days=30),
                'hora': time(10, 0),
                'motivo': 'Control anual y vacunación',
                'peso_visita': 28.20,
                'temperatura': 38.5,
                'diagnostico': 'Animal sano. Vacunación al día.',
                'tratamiento': 'Sextuple aplicada. Antiparasitario interno.',
                'requiere_seguimiento': 'no',
                'fecha_proxima_visita': None,
                'indicaciones_tutor': 'Próxima vacuna en 12 meses.',
                'estado': 'completada',
            },
            {
                'paciente': pac('Max'),
                'veterinario': vets[1],
                'fecha': hoy - timedelta(days=20),
                'hora': time(11, 30),
                'motivo': 'Prurito generalizado y pérdida de pelo',
                'peso_visita': 33.80,
                'temperatura': 38.8,
                'diagnostico': 'Alergia alimentaria confirmada.',
                'tratamiento': 'Cambio de dieta a cordero. Antihistamínico 5 días.',
                'requiere_seguimiento': 'programada',
                'fecha_proxima_visita': hoy + timedelta(days=10),
                'indicaciones_tutor': 'No ofrecer alimentos con pollo. Revisar etiquetas.',
                'estado': 'completada',
            },
            {
                'paciente': pac('Rocko'),
                'veterinario': vets[0],
                'fecha': hoy - timedelta(days=15),
                'hora': time(9, 0),
                'motivo': 'Control displasia de cadera',
                'peso_visita': 37.50,
                'temperatura': 38.6,
                'diagnostico': 'Displasia bilateral leve-moderada. Estable.',
                'tratamiento': 'Continuar Meloxicam. Agregar Condroitín 500mg/día.',
                'requiere_seguimiento': 'programada',
                'fecha_proxima_visita': hoy + timedelta(days=60),
                'indicaciones_tutor': 'Evitar escaleras. Superficie antideslizante en casa.',
                'estado': 'completada',
            },
            {
                'paciente': pac('Michi'),
                'veterinario': vets[2],
                'fecha': hoy - timedelta(days=10),
                'hora': time(14, 0),
                'motivo': 'Castración',
                'peso_visita': 4.10,
                'temperatura': 38.4,
                'diagnostico': 'Cirugía sin complicaciones.',
                'tratamiento': 'Amoxicilina 50mg c/12h por 5 días. Collar isabelino.',
                'requiere_seguimiento': 'programada',
                'fecha_proxima_visita': hoy + timedelta(days=7),
                'indicaciones_tutor': 'Mantener collar. Revisar herida diariamente.',
                'estado': 'completada',
            },
            # Consultas de hoy / en curso
            {
                'paciente': pac('Rex'),
                'veterinario': vets[0],
                'fecha': hoy,
                'hora': time(9, 30),
                'motivo': 'Dermatitis — revisión urgente y posible infección',
                'peso_visita': 22.10,
                'temperatura': 39.2,
                'diagnostico': '',
                'tratamiento': '',
                'requiere_seguimiento': 'urgente',
                'fecha_proxima_visita': None,
                'indicaciones_tutor': '',
                'estado': 'en_curso',
            },
            {
                'paciente': pac('Copito'),
                'veterinario': vets[1],
                'fecha': hoy,
                'hora': time(11, 0),
                'motivo': 'Primera consulta y vacunación cachorro',
                'peso_visita': 5.80,
                'temperatura': None,
                'diagnostico': '',
                'tratamiento': '',
                'requiere_seguimiento': 'no',
                'fecha_proxima_visita': None,
                'indicaciones_tutor': '',
                'estado': 'pendiente',
            },
            # Consultas futuras / pendientes
            {
                'paciente': pac('Max'),
                'veterinario': vets[1],
                'fecha': hoy + timedelta(days=10),
                'hora': time(10, 30),
                'motivo': 'Revisión alergia — seguimiento dieta',
                'peso_visita': None,
                'temperatura': None,
                'diagnostico': '',
                'tratamiento': '',
                'requiere_seguimiento': 'no',
                'fecha_proxima_visita': None,
                'indicaciones_tutor': '',
                'estado': 'pendiente',
            },
            {
                'paciente': pac('Michi'),
                'veterinario': vets[2],
                'fecha': hoy + timedelta(days=7),
                'hora': time(15, 0),
                'motivo': 'Retiro de puntos post-castración',
                'peso_visita': None,
                'temperatura': None,
                'diagnostico': '',
                'tratamiento': '',
                'requiere_seguimiento': 'no',
                'fecha_proxima_visita': None,
                'indicaciones_tutor': '',
                'estado': 'pendiente',
            },
            {
                'paciente': pac('Rocko'),
                'veterinario': vets[0],
                'fecha': hoy + timedelta(days=60),
                'hora': time(9, 0),
                'motivo': 'Control radiológico displasia de cadera',
                'peso_visita': None,
                'temperatura': None,
                'diagnostico': '',
                'tratamiento': '',
                'requiere_seguimiento': 'no',
                'fecha_proxima_visita': None,
                'indicaciones_tutor': '',
                'estado': 'pendiente',
            },
            {
                'paciente': pac('Pelusa'),
                'veterinario': vets[2],
                'fecha': hoy + timedelta(days=3),
                'hora': time(16, 0),
                'motivo': 'Vacunación anual triple felina',
                'peso_visita': None,
                'temperatura': None,
                'diagnostico': '',
                'tratamiento': '',
                'requiere_seguimiento': 'no',
                'fecha_proxima_visita': None,
                'indicaciones_tutor': '',
                'estado': 'pendiente',
            },
        ]

        for datos in consultas:
            Consulta.objects.get_or_create(
                paciente=datos['paciente'],
                fecha=datos['fecha'],
                hora=datos['hora'],
                motivo=datos['motivo'],
                defaults=datos,
            )

    # ------------------------------------------------------------------
    def _crear_masivos(self, factor, vets):
        """Genera volumen adicional de datos de prueba (determinista).

        Crea ~5*factor tutores nuevos, cada uno con 1-3 mascotas, y para
        cada mascota vacunas y 0-3 consultas. Con factor=20 ≈ 100 tutores,
        ~200 pacientes y ~400 consultas, además de los datos curados.
        """
        self.stdout.write(f'Generando datos masivos (x{factor})...')
        rnd = random.Random(20260601)  # semilla fija → idempotente

        nombres = [
            'Sofía', 'Mateo', 'Emma', 'Benjamín', 'Martina', 'Vicente', 'Florencia',
            'Agustín', 'Antonia', 'Tomás', 'Josefa', 'Maximiliano', 'Catalina', 'Lucas',
            'Emilia', 'Joaquín', 'Amanda', 'Gabriel', 'Trinidad', 'Diego', 'Javiera',
            'Cristóbal', 'Constanza', 'Matías', 'Fernanda', 'Nicolás', 'Valeria', 'Ignacio',
        ]
        apellidos = [
            'González', 'Muñoz', 'Rojas', 'Díaz', 'Pérez', 'Soto', 'Contreras', 'Silva',
            'Martínez', 'Sepúlveda', 'Morales', 'Rodríguez', 'López', 'Fuentes', 'Hernández',
            'Torres', 'Araya', 'Flores', 'Espinoza', 'Castillo', 'Tapia', 'Reyes', 'Gutiérrez',
        ]
        ciudades = [
            'Santiago', 'Las Condes', 'Ñuñoa', 'Providencia', 'Maipú', 'La Florida',
            'Puente Alto', 'Vitacura', 'San Miguel', 'Peñalolén', 'Macul', 'Recoleta',
        ]
        razas = {
            'canino': ['Mestizo', 'Labrador', 'Golden Retriever', 'Poodle', 'Bulldog Francés',
                       'Pastor Alemán', 'Beagle', 'Chihuahua', 'Cocker Spaniel', 'Husky'],
            'felino': ['Mestizo', 'Siamés', 'Persa', 'Angora', 'Maine Coon', 'Bengalí'],
            'ave': ['Canario', 'Periquito', 'Agapornis', 'Cacatúa'],
            'roedor': ['Hámster', 'Cobayo', 'Conejo', 'Chinchilla'],
            'reptil': ['Tortuga', 'Iguana', 'Gecko'],
            'otro': ['Hurón', 'Erizo'],
        }
        nombres_mascota = [
            'Toby', 'Rocky', 'Coco', 'Lola', 'Bella', 'Simba', 'Nina', 'Thor', 'Maya',
            'Bruno', 'Kira', 'Zeus', 'Mia', 'Duke', 'Frida', 'Oso', 'Canela', 'Negro',
            'Manchas', 'Pelusa', 'Gordo', 'Princesa', 'Chico', 'Luna', 'Sol', 'Estrella',
        ]
        especies = ['canino'] * 6 + ['felino'] * 4 + ['ave', 'roedor', 'reptil', 'otro']
        estados = ['activo'] * 7 + ['seguimiento'] * 2 + ['urgente', 'inactivo']
        motivos = [
            'Control sano anual', 'Vacunación', 'Desparasitación', 'Consulta por vómitos',
            'Cojera en pata trasera', 'Control de peso', 'Limpieza dental', 'Otitis',
            'Dermatitis', 'Castración', 'Chequeo geriátrico', 'Herida superficial',
            'Diarrea aguda', 'Control post-operatorio', 'Decaimiento general',
        ]

        hoy = date.today()
        n_tutores = 5 * factor

        for i in range(n_tutores):
            nom = f'{rnd.choice(nombres)} {rnd.choice(apellidos)}'
            rut = '2{:01d}.{:03d}.{:03d}-{}'.format(
                i // 1000000 % 10, (i // 1000) % 1000, i % 1000, rnd.choice('0123456789K')
            )
            tutor, _ = Tutor.objects.get_or_create(
                rut=rut,
                defaults={
                    'nombre': nom,
                    'telefono': '+56 9 {:04d} {:04d}'.format(rnd.randint(2000, 9999), rnd.randint(1000, 9999)),
                    'email': '{}@example.cl'.format(nom.lower().replace(' ', '.').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')),
                    'direccion': '{} {}'.format(rnd.choice(['Av.', 'Calle', 'Pasaje']), rnd.randint(100, 9999)),
                    'ciudad': rnd.choice(ciudades),
                },
            )

            for _m in range(rnd.randint(1, 3)):
                especie = rnd.choice(especies)
                sexo = rnd.choice(['M', 'F'])
                edad_dias = rnd.randint(120, 365 * 14)
                peso = {
                    'canino': round(rnd.uniform(3, 45), 2),
                    'felino': round(rnd.uniform(2.5, 7), 2),
                    'ave': round(rnd.uniform(0.02, 0.5), 2),
                    'roedor': round(rnd.uniform(0.05, 3), 2),
                    'reptil': round(rnd.uniform(0.1, 5), 2),
                    'otro': round(rnd.uniform(0.5, 4), 2),
                }[especie]
                pac, creado = Paciente.objects.get_or_create(
                    nombre=rnd.choice(nombres_mascota),
                    tutor=tutor,
                    defaults={
                        'especie': especie,
                        'raza': rnd.choice(razas[especie]),
                        'sexo': sexo,
                        'fecha_nacimiento': hoy - timedelta(days=edad_dias),
                        'peso': peso,
                        'estado': rnd.choice(estados),
                    },
                )
                if not creado:
                    continue

                # Vacunas
                if especie == 'canino':
                    for nombre, da, dp in [('Séxtuple', -300, 65), ('Antirrábica', -150, 215)]:
                        Vacuna.objects.get_or_create(
                            paciente=pac, nombre=nombre,
                            defaults={'fecha_aplicacion': hoy + timedelta(days=da),
                                      'proxima_dosis': hoy + timedelta(days=dp)},
                        )
                elif especie == 'felino':
                    Vacuna.objects.get_or_create(
                        paciente=pac, nombre='Triple Felina',
                        defaults={'fecha_aplicacion': hoy - timedelta(days=200),
                                  'proxima_dosis': hoy + timedelta(days=165)},
                    )

                # Consultas (0-3)
                for _c in range(rnd.randint(0, 3)):
                    offset = rnd.randint(-180, 30)
                    estado = 'completada' if offset < 0 else rnd.choice(['pendiente', 'en_curso'])
                    Consulta.objects.get_or_create(
                        paciente=pac,
                        fecha=hoy + timedelta(days=offset),
                        hora=time(rnd.randint(9, 18), rnd.choice([0, 15, 30, 45])),
                        motivo=rnd.choice(motivos),
                        defaults={
                            'veterinario': rnd.choice(vets),
                            'peso_visita': peso,
                            'temperatura': round(rnd.uniform(37.5, 39.5), 1),
                            'estado': estado,
                            'diagnostico': 'Evaluación clínica completada.' if estado == 'completada' else '',
                            'tratamiento': 'Tratamiento indicado según hallazgos.' if estado == 'completada' else '',
                            'requiere_seguimiento': rnd.choice(['no', 'no', 'programada']),
                        },
                    )

    # ------------------------------------------------------------------
    def _crear_consultas_masivas(self, objetivo, vets):
        """Rellena consultas hasta alcanzar 'objetivo', con fechas
        distribuidas entre el 1 de enero de 2026 y hoy. Usa bulk_create
        para eficiencia; idempotente respecto al total objetivo."""
        pacientes = list(Paciente.objects.all())
        if not pacientes or not vets:
            return

        actuales = Consulta.objects.count()
        faltan = objetivo - actuales
        if faltan <= 0:
            self.stdout.write(f'Consultas ya en {actuales} (objetivo {objetivo}); nada que agregar.')
            return

        self.stdout.write(f'Generando {faltan} consultas (ene-2026 → hoy)...')
        rnd = random.Random(5050)
        inicio = date(2026, 1, 1)
        hoy = date.today()
        rango = max((hoy - inicio).days, 1)

        motivos = [
            'Control sano anual', 'Vacunación', 'Desparasitación', 'Consulta por vómitos',
            'Cojera en pata trasera', 'Control de peso', 'Limpieza dental', 'Otitis',
            'Dermatitis', 'Castración', 'Chequeo geriátrico', 'Herida superficial',
            'Diarrea aguda', 'Control post-operatorio', 'Decaimiento general',
            'Examen pre-quirúrgico', 'Revisión oftalmológica', 'Control de gestación',
        ]

        nuevas = []
        for _ in range(faltan):
            pac = rnd.choice(pacientes)
            f = inicio + timedelta(days=rnd.randint(0, rango))
            completada = f < hoy
            seguimiento = rnd.choice(['no', 'no', 'no', 'programada', 'urgente'])
            prox = None
            if seguimiento != 'no':
                prox = f + timedelta(days=rnd.randint(7, 90))
            nuevas.append(Consulta(
                paciente=pac,
                veterinario=rnd.choice(vets),
                fecha=f,
                hora=time(rnd.randint(9, 18), rnd.choice([0, 15, 30, 45])),
                motivo=rnd.choice(motivos),
                peso_visita=round(rnd.uniform(2, 45), 2),
                temperatura=round(rnd.uniform(37.5, 39.5), 1),
                estado='completada' if completada else rnd.choice(['pendiente', 'en_curso']),
                diagnostico='Evaluación clínica completada.' if completada else '',
                tratamiento='Tratamiento indicado según hallazgos.' if completada else '',
                requiere_seguimiento=seguimiento,
                fecha_proxima_visita=prox,
            ))

        Consulta.objects.bulk_create(nuevas, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'  + {len(nuevas)} consultas creadas.'))
