from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalogo.models import Prenda
from usuarios.models import Usuario
from .models import Conversacion, Mensaje


@login_required
def iniciar_conversacion(request, prenda_id):
    """Cliente inicia conversación desde detalle de prenda."""
    prenda = get_object_or_404(Prenda, id=prenda_id)

    conversacion, _ = Conversacion.objects.get_or_create(
        prenda  = prenda,
        cliente = request.user,
    )
    return redirect('ver_conversacion', conversacion_id=conversacion.id)


@login_required
def ver_conversacion(request, conversacion_id):
    """Vista del hilo de mensajes."""
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)

    # Solo el cliente de la conversación o un admin puede verla
    if request.user != conversacion.cliente and request.user.perfil != 'administrador':
        return render(request, 'mensajeria/sin_acceso.html')

    # Marcar mensajes como leídos
    conversacion.mensajes.exclude(remitente=request.user).update(leido=True)

    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            Mensaje.objects.create(
                conversacion = conversacion,
                remitente    = request.user,
                contenido    = contenido,
            )
        return redirect('ver_conversacion', conversacion_id=conversacion.id)

    mensajes_list = conversacion.mensajes.select_related('remitente').all()
    return render(request, 'mensajeria/conversacion.html', {
        'conversacion': conversacion,
        'mensajes'    : mensajes_list,
    })


@login_required
def lista_conversaciones(request):
    """Admin ve todas las conversaciones."""
    if request.user.perfil != 'administrador':
        return render(request, 'mensajeria/sin_acceso.html')

    conversaciones = Conversacion.objects.select_related(
        'prenda', 'cliente'
    ).prefetch_related('mensajes').order_by('-creada_en')

    return render(request, 'mensajeria/lista.html', {'conversaciones': conversaciones})


@login_required
def mis_conversaciones(request):
    """Cliente ve sus propias conversaciones."""
    conversaciones = Conversacion.objects.filter(
        cliente=request.user
    ).select_related('prenda').prefetch_related('mensajes').order_by('-creada_en')

    return render(request, 'mensajeria/mis_conversaciones.html', {'conversaciones': conversaciones})