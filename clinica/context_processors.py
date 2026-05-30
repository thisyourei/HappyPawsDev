from .models import PerfilUsuario


def perfil_context(request):
    if not request.user.is_authenticated:
        return {'perfil': None}
    try:
        return {'perfil': request.user.perfil}
    except PerfilUsuario.DoesNotExist:
        if request.user.is_superuser:
            perfil = PerfilUsuario.objects.create(user=request.user, rol='administrador')
            return {'perfil': perfil}
        return {'perfil': None}
