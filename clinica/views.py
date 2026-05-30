import calendar
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Max

from .models import Paciente, Tutor, Consulta, Veterinario
from .forms import PacienteForm, TutorForm, ConsultaForm


def index(request):
    hoy = timezone.localdate()

    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')
        if form_type == 'paciente':
            form = PacienteForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Paciente registrado correctamente.')
                return redirect('index')
        elif form_type == 'tutor':
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
                return redirect('index')

    consultas_mes = Consulta.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month,
    ).count()

    context = {
        'total_pacientes': Paciente.objects.filter(estado__in=['activo', 'seguimiento', 'urgente']).count(),
        'total_tutores': Tutor.objects.count(),
        'citas_hoy': Consulta.objects.filter(fecha=hoy).count(),
        'citas_pendientes': Consulta.objects.filter(fecha=hoy, estado='pendiente').count(),
        'seguimientos': Paciente.objects.filter(estado='seguimiento').count(),
        'urgentes': Paciente.objects.filter(estado='urgente').count(),
        'citas_hoy_list': (
            Consulta.objects
            .filter(fecha=hoy)
            .select_related('paciente__tutor', 'veterinario')
            .order_by('hora')
        ),
        'pacientes_recientes': (
            Paciente.objects
            .select_related('tutor')
            .order_by('-creado')[:5]
        ),
        'caninos': Paciente.objects.filter(especie='canino').count(),
        'felinos': Paciente.objects.filter(especie='felino').count(),
        'otros': Paciente.objects.exclude(especie__in=['canino', 'felino']).count(),
        'pacientes': (
            Paciente.objects
            .select_related('tutor')
            .annotate(ultima_visita=Max('consultas__fecha'))
            .order_by('-creado')
        ),
        'tutores': (
            Tutor.objects
            .prefetch_related('pacientes')
            .annotate(ultima_visita=Max('pacientes__consultas__fecha'))
            .order_by('nombre')
        ),
        'consultas': (
            Consulta.objects
            .select_related('paciente', 'veterinario')
            .order_by('-fecha', '-hora')[:20]
        ),
        'consultas_mes': consultas_mes,
        'promedio_diario': round(consultas_mes / max(hoy.day, 1), 1),
        'consultas_pendientes_hoy': Consulta.objects.filter(fecha=hoy, estado='pendiente').count(),
        'veterinarios': Veterinario.objects.all(),
    }
    return render(request, 'clinica/index.html', context)
