from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    ConsultaEditForm,
    ConsultaForm,
    CrearUsuarioForm,
    PacienteEditForm,
    PacienteForm,
    TutorForm,
)
from .models import Consulta, Paciente, PerfilUsuario, Tutor, Vacuna, Veterinario


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_create_perfil(user):
    try:
        return user.perfil
    except PerfilUsuario.DoesNotExist:
        if user.is_superuser:
            return PerfilUsuario.objects.create(user=user, rol='administrador')
        return None



# ── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    error = None
    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_input, password=password)
        if user is None:
            try:
                u = User.objects.get(email=username_input)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            perfil = _get_or_create_perfil(user)
            if perfil is None:
                error = 'Tu cuenta no tiene un perfil asignado. Contacta al administrador.'
            else:
                login(request, user)
                return redirect('index')
        else:
            error = 'Correo o contraseña incorrectos.'

    return render(request, 'clinica/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Vista principal ───────────────────────────────────────────────────────────

@login_required
def index(request):
    perfil = _get_or_create_perfil(request.user)
    if perfil is None:
        logout(request)
        return redirect('login')

    hoy = timezone.localdate()
    semana = hoy + timedelta(days=7)

    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')

        if form_type == 'paciente':
            if not perfil.puede_registrar:
                messages.error(request, 'Sin permiso para registrar pacientes.')
                return redirect('index')
            form = PacienteForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Paciente registrado correctamente.')
                return redirect('index')

        elif form_type == 'tutor':
            if not perfil.puede_registrar:
                messages.error(request, 'Sin permiso para registrar tutores.')
                return redirect('index')
            form = TutorForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tutor registrado correctamente.')
                return redirect('index')

        elif form_type == 'consulta':
            form = ConsultaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Consulta guardada correctamente.')
                return redirect(f"{reverse('index')}?pantalla=consultas")

        elif form_type == 'usuario':
            if not perfil.puede_gestionar_usuarios:
                messages.error(request, 'Sin permiso para crear usuarios.')
                return redirect('index')
            roles = perfil.roles_que_puede_crear
            form = CrearUsuarioForm(request.POST, roles_permitidos=roles)
            if form.is_valid():
                data = form.cleaned_data
                nuevo_user = User.objects.create_user(
                    username=data['email'], email=data['email'],
                    password=data['password'],
                    first_name=data['nombre'], last_name=data['apellido'],
                )
                PerfilUsuario.objects.create(user=nuevo_user, rol=data['rol'])
                if data['rol'] == 'veterinario':
                    Veterinario.objects.get_or_create(nombre=f"{data['nombre']} {data['apellido']}")
                messages.success(
                    request,
                    f"Usuario {data['nombre']} {data['apellido']} creado como {dict(PerfilUsuario.ROL)[data['rol']]}."
                )
                return redirect(f"{reverse('index')}?pantalla=usuarios")

    # ── Contexto ─────────────────────────────────────────────────────────────
    consultas_mes = Consulta.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month).count()

    # Consultas enriquecidas para el panel de Consultas
    base_qs = Consulta.objects.select_related('paciente', 'veterinario').order_by('fecha', 'hora')

    consultas_hoy     = base_qs.filter(fecha=hoy)
    consultas_proximas = base_qs.filter(fecha__gt=hoy, fecha__lte=semana)
    consultas_historial = (
        Consulta.objects
        .filter(fecha__lt=hoy)
        .select_related('paciente', 'veterinario')
        .order_by('-fecha', '-hora')[:40]
    )

    # Seguimientos con fecha inminente o vencida
    seguimientos_pendientes = (
        Consulta.objects
        .filter(
            requiere_seguimiento__in=['programada', 'urgente'],
            fecha_proxima_visita__isnull=False,
            fecha_proxima_visita__lte=semana,
        )
        .select_related('paciente')
        .order_by('requiere_seguimiento', 'fecha_proxima_visita')
    )

    # Saludo según hora del día
    hora_local = timezone.localtime().hour
    if hora_local < 12:
        saludo = 'Buenos días'
    elif hora_local < 20:
        saludo = 'Buenas tardes'
    else:
        saludo = 'Buenas noches'

    # Datos exclusivos del nuevo Inicio
    vacunas_vencidas = (
        Vacuna.objects
        .filter(proxima_dosis__lt=hoy, proxima_dosis__isnull=False)
        .select_related('paciente')
        .order_by('proxima_dosis')[:6]
    )
    proximas_48h = (
        Consulta.objects
        .filter(fecha__in=[hoy + timedelta(1), hoy + timedelta(2)])
        .select_related('paciente', 'veterinario')
        .order_by('fecha', 'hora')
    )
    seguimientos_vencidos = seguimientos_pendientes.filter(
        fecha_proxima_visita__lt=hoy
    ).count()

    # Stats detalladas para el panel de consultas
    stats_consultas = {
        'hoy_total':      consultas_hoy.count(),
        'hoy_pendientes': consultas_hoy.filter(estado='pendiente').count(),
        'hoy_en_curso':   consultas_hoy.filter(estado='en_curso').count(),
        'hoy_completadas':consultas_hoy.filter(estado='completada').count(),
        'semana':         consultas_proximas.count(),
        'mes':            consultas_mes,
    }

    usuarios_qs = []
    if perfil.puede_gestionar_usuarios:
        usuarios_qs = (
            PerfilUsuario.objects
            .select_related('user')
            .order_by('rol', 'user__first_name')
        )

    context = {
        'perfil': perfil,
        'hoy': hoy,
        # inicio — datos del día
        'saludo':                saludo,
        'citas_hoy_list': (
            Consulta.objects
            .filter(fecha=hoy)
            .select_related('paciente__tutor', 'veterinario')
            .order_by('hora')
        ),
        'vacunas_vencidas':      vacunas_vencidas,
        'proximas_48h':          proximas_48h,
        'seguimientos_vencidos': seguimientos_vencidos,
        # pacientes panel
        'total_pacientes': Paciente.objects.filter(estado__in=['activo', 'seguimiento', 'urgente']).count(),
        # pacientes
        'caninos': Paciente.objects.filter(especie='canino').count(),
        'felinos': Paciente.objects.filter(especie='felino').count(),
        'otros':   Paciente.objects.exclude(especie__in=['canino', 'felino']).count(),
        'pacientes': (
            Paciente.objects
            .select_related('tutor')
            .annotate(ultima_visita=Max('consultas__fecha'))
            .order_by('-creado')
        ),
        # tutores
        'tutores': (
            Tutor.objects
            .prefetch_related('pacientes')
            .annotate(ultima_visita=Max('pacientes__consultas__fecha'))
            .order_by('nombre')
        ),
        # consultas — panel enriquecido
        'consultas_hoy':          consultas_hoy,
        'consultas_proximas':     consultas_proximas,
        'consultas_historial':    consultas_historial,
        'seguimientos_pendientes':seguimientos_pendientes,
        'stats_consultas':        stats_consultas,
        'veterinarios':           Veterinario.objects.all(),
        # usuarios
        'usuarios': usuarios_qs,
        'roles_que_puede_crear': perfil.roles_que_puede_crear,
    }
    return render(request, 'clinica/index.html', context)


# ── Consulta detalle / edición ────────────────────────────────────────────────

@login_required
def consulta_detalle(request, pk):
    perfil = _get_or_create_perfil(request.user)
    if perfil is None:
        return redirect('login')

    consulta = get_object_or_404(
        Consulta.objects.select_related('paciente__tutor', 'veterinario'),
        pk=pk,
    )

    if request.method == 'POST' and perfil.puede_registrar:
        form = ConsultaEditForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta actualizada correctamente.')
            return redirect('consulta_detalle', pk=pk)
    else:
        form = ConsultaEditForm(instance=consulta)

    # Historial del mismo paciente (excluye la consulta actual)
    historial_paciente = (
        Consulta.objects
        .filter(paciente=consulta.paciente)
        .exclude(pk=pk)
        .select_related('veterinario')
        .order_by('-fecha', '-hora')
    )

    context = {
        'perfil':           perfil,
        'hoy':              timezone.localdate(),
        'consulta':         consulta,
        'form':             form,
        'historial':        historial_paciente,
        'veterinarios':     Veterinario.objects.all(),
        'puede_editar':     perfil.puede_registrar,
        'total_consultas':  historial_paciente.count() + 1,
    }
    return render(request, 'clinica/consulta_detalle.html', context)


# ── Paciente / Tutor edición ──────────────────────────────────────────────────

@login_required
def paciente_editar(request, pk):
    perfil = _get_or_create_perfil(request.user)
    if perfil is None:
        return redirect('login')
    if not perfil.puede_registrar:
        messages.error(request, 'Sin permiso para editar pacientes.')
        return redirect('index')

    paciente = get_object_or_404(Paciente.objects.select_related('tutor'), pk=pk)

    if request.method == 'POST':
        form = PacienteEditForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Paciente {paciente.nombre} actualizado correctamente.')
            return redirect(f"{reverse('index')}?pantalla=pacientes")
    else:
        form = PacienteEditForm(instance=paciente)

    context = {
        'perfil':    perfil,
        'paciente':  paciente,
        'form':      form,
        'tutores':   Tutor.objects.order_by('nombre'),
        'consultas': (
            Consulta.objects
            .filter(paciente=paciente)
            .select_related('veterinario')
            .order_by('-fecha', '-hora')
        ),
    }
    return render(request, 'clinica/paciente_editar.html', context)


@login_required
def tutor_editar(request, pk):
    perfil = _get_or_create_perfil(request.user)
    if perfil is None:
        return redirect('login')
    if not perfil.puede_registrar:
        messages.error(request, 'Sin permiso para editar tutores.')
        return redirect('index')

    tutor = get_object_or_404(Tutor, pk=pk)

    if request.method == 'POST':
        form = TutorForm(request.POST, instance=tutor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tutor {tutor.nombre} actualizado correctamente.')
            return redirect(f"{reverse('index')}?pantalla=tutores")
    else:
        form = TutorForm(instance=tutor)

    context = {
        'perfil':    perfil,
        'tutor':     tutor,
        'form':      form,
        'pacientes': tutor.pacientes.all(),
    }
    return render(request, 'clinica/tutor_editar.html', context)


@login_required
def consulta_estado(request, pk):
    """Cambio rápido de estado desde la lista (POST only)."""
    if request.method == 'POST' and _get_or_create_perfil(request.user):
        consulta = get_object_or_404(Consulta, pk=pk)
        nuevo = request.POST.get('estado', '')
        estados_validos = [e[0] for e in Consulta.ESTADO]
        if nuevo in estados_validos:
            consulta.estado = nuevo
            consulta.save(update_fields=['estado'])
    return redirect(request.META.get('HTTP_REFERER') or 'index')
