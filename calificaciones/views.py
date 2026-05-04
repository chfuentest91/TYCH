from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from catalogo.models import Prenda
from transacciones.models import Orden
from .models import CalificacionPrenda, CalificacionVendedor


def _verificar_compra(usuario, prenda):
    """Verifica que el usuario compró la prenda."""
    return Orden.objects.filter(
        usuario=usuario,
        prenda=prenda,
        estado='aprobada'
    ).exists()


@login_required
def calificar_prenda(request, prenda_id):
    prenda = get_object_or_404(Prenda, id=prenda_id)

    if not _verificar_compra(request.user, prenda):
        messages.error(request, 'Solo puedes calificar prendas que hayas comprado.')
        return redirect(f'/catalogo/detalle/{prenda_id}/')

    ya_califico = CalificacionPrenda.objects.filter(
        prenda=prenda, comprador=request.user
    ).exists()

    if ya_califico:
        messages.info(request, 'Ya calificaste esta prenda.')
        return redirect(f'/catalogo/detalle/{prenda_id}/')

    if request.method == 'POST':
        puntuacion = int(request.POST.get('puntuacion', 0))
        comentario = request.POST.get('comentario', '').strip()

        if 1 <= puntuacion <= 5:
            CalificacionPrenda.objects.create(
                prenda=prenda,
                comprador=request.user,
                puntuacion=puntuacion,
                comentario=comentario,
            )
            messages.success(request, '¡Gracias por tu calificación!')
        return redirect(f'/catalogo/detalle/{prenda_id}/')

    return render(request, 'calificaciones/calificar_prenda.html', {'prenda': prenda})


@login_required
def calificar_vendedor(request, prenda_id):
    prenda   = get_object_or_404(Prenda, id=prenda_id)
    vendedor = prenda.admin

    if not _verificar_compra(request.user, prenda):
        messages.error(request, 'Solo puedes calificar al vendedor si compraste esta prenda.')
        return redirect(f'/catalogo/detalle/{prenda_id}/')

    ya_califico = CalificacionVendedor.objects.filter(
        vendedor=vendedor, comprador=request.user, prenda=prenda
    ).exists()

    if ya_califico:
        messages.info(request, 'Ya calificaste al vendedor por esta prenda.')
        return redirect(f'/catalogo/detalle/{prenda_id}/')

    if request.method == 'POST':
        puntuacion = int(request.POST.get('puntuacion', 0))
        comentario = request.POST.get('comentario', '').strip()

        if 1 <= puntuacion <= 5:
            CalificacionVendedor.objects.create(
                vendedor=vendedor,
                comprador=request.user,
                prenda=prenda,
                puntuacion=puntuacion,
                comentario=comentario,
            )
            messages.success(request, '¡Gracias por calificar al vendedor!')
        return redirect(f'/catalogo/detalle/{prenda_id}/')

    promedio = CalificacionVendedor.objects.filter(
        vendedor=vendedor
    ).aggregate(Avg('puntuacion'))['puntuacion__avg']

    return render(request, 'calificaciones/calificar_vendedor.html', {
        'prenda'  : prenda,
        'vendedor': vendedor,
        'promedio': promedio,
    })