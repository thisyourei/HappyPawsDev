from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import InformeForm, MascotaForm, TutorForm, VeterinarioForm
from .models import Informe, Mascota, Tutor, Veterinario

def dashboard(request):
    pacientes = Mascota.objects.order_by('-creado')[:6]
    tutores = Tutor.objects.count()
    veterinarios = Veterinario.objects.count()
    consultas = Informe.objects.count()
    contexto = {
        'pacientes': pacientes,
        'tutores': tutores,
        'veterinarios': veterinarios,
        'consultas': consultas,
    }
    return render(request, 'clinic/dashboard.html', contexto)

def pacientes(request):
    mascotas = Mascota.objects.select_related('tutor', 'veterinario').order_by('-creado')
    return render(request, 'clinic/pacientes.html', {'mascotas': mascotas})

def tutores(request):
    tutores = Tutor.objects.order_by('-creado')
    return render(request, 'clinic/tutores.html', {'tutores': tutores})

def veterinarios(request):
    veterinarios = Veterinario.objects.order_by('-creado')
    return render(request, 'clinic/veterinarios.html', {'veterinarios': veterinarios})

def informes(request):
    informes = Informe.objects.select_related('mascota', 'veterinario').order_by('-fecha')
    return render(request, 'clinic/informes.html', {'informes': informes})

def mascota_detalle(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    informes = mascota.informes.order_by('-fecha')
    return render(request, 'clinic/mascota_detalle.html', {'mascota': mascota, 'informes': informes})

def nuevo_registro(request):
    tipo = request.GET.get('tipo', 'mascota')
    current_form = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mascota':
            form = MascotaForm(request.POST, prefix='mascota')
            if form.is_valid():
                form.save()
                return redirect(reverse('pacientes'))
            current_form = form
        elif action == 'tutor':
            form = TutorForm(request.POST, prefix='tutor')
            if form.is_valid():
                form.save()
                return redirect(reverse('tutores'))
            current_form = form
        elif action == 'veterinario':
            form = VeterinarioForm(request.POST, prefix='veterinario')
            if form.is_valid():
                form.save()
                return redirect(reverse('veterinarios'))
            current_form = form
        elif action == 'informe':
            form = InformeForm(request.POST, prefix='informe')
            if form.is_valid():
                form.save()
                return redirect(reverse('informes'))
            current_form = form
    else:
        if tipo == 'mascota':
            current_form = MascotaForm(prefix='mascota')
        elif tipo == 'tutor':
            current_form = TutorForm(prefix='tutor')
        elif tipo == 'veterinario':
            current_form = VeterinarioForm(prefix='veterinario')
        elif tipo == 'informe':
            current_form = InformeForm(prefix='informe')
    
    return render(request, 'clinic/nuevo.html', {'current_form': current_form, 'tipo': tipo})
