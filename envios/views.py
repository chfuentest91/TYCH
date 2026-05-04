from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from transacciones.models import Orden
from .models import Envio


@login_required
def lista_envios(request):
    """Vista para administrador — lista todos los envíos."""
    if request.user.perfil != 'administrador':
        return render(request, 'envios/sin_acceso.html')

    envios = Envio.objects.select_related(
        'orden', 'orden__prenda', 'orden__usuario'
    ).order_by('-fecha_actualizacion')

    return render(request, 'envios/lista.html', {'envios': envios})


@login_required
def actualizar_estado(request, envio_id):
    """Admin actualiza el estado del envío."""
    if request.user.perfil != 'administrador':
        return render(request, 'envios/sin_acceso.html')

    envio = get_object_or_404(Envio, id=envio_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['pendiente', 'en_camino', 'entregado']:
            envio.estado          = nuevo_estado
            envio.actualizado_por = request.user
            envio.save()
            messages.success(request, f'Estado actualizado a "{envio.get_estado_display()}".')
        return redirect('lista_envios')

    return render(request, 'envios/actualizar.html', {'envio': envio})


@login_required
def mis_envios(request):
    """Vista para cliente — ve sus envíos desde su perfil."""
    ordenes_ids = Orden.objects.filter(
        usuario=request.user, estado='aprobada'
    ).values_list('id', flat=True)

    envios = Envio.objects.filter(
        orden_id__in=ordenes_ids
    ).select_related('orden__prenda').order_by('-fecha_actualizacion')

    return render(request, 'envios/mis_envios.html', {'envios': envios})