from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime as dt

from tych import transbank_service
from catalogo.models import Prenda
from .models import Orden


@csrf_exempt
def iniciar_pago(request, prenda_id):
    prenda = get_object_or_404(Prenda, id=prenda_id, estado='disponible')
    usuario = request.user

    buy_order  = f"TYCH-{prenda_id}-{int(timezone.now().timestamp())}"
    session_id = str(usuario.id)
    amount     = int(prenda.precio)
    return_url = request.build_absolute_uri('/transacciones/commit-pago/')

    response = transbank_service.crear_transaccion(
        buy_order=buy_order,
        session_id=session_id,
        amount=amount,
        return_url=return_url
    )

    if response.status_code == 200:
        tb_data = response.json()

        Orden.objects.create(
            prenda    = prenda,
            usuario   = usuario,
            buy_order = buy_order,
            monto     = amount,
            token_ws  = tb_data['token'],
            estado    = 'pendiente',
        )

        return render(request, 'transacciones/send-pay.html', {
            'transbank': tb_data,
            'amount'   : amount,
        })
    else:
        return render(request, 'transacciones/commit-pay.html', {
            'resultado': {'estado': 'ERROR', 'mensaje': 'No se pudo iniciar el pago. Intenta nuevamente.'}
        })


@csrf_exempt
def commit_pago(request):
    token_ws = request.GET.get('token_ws') or request.POST.get('token_ws')

    if not token_ws:
        return render(request, 'transacciones/commit-pay.html', {
            'resultado': {'estado': 'CANCELADO', 'mensaje': 'El pago fue cancelado.'}
        })

    try:
        orden = Orden.objects.get(token_ws=token_ws)
    except Orden.DoesNotExist:
        return render(request, 'transacciones/commit-pay.html', {
            'resultado': {'estado': 'ERROR', 'mensaje': 'Orden no encontrada.'}
        })

    response = transbank_service.confirmar_transaccion(token_ws)

    if response.status_code == 200:
        data          = response.json()
        status        = data.get('status')
        response_code = data.get('response_code')

        if status == 'AUTHORIZED' and response_code == 0:
            # ✅ Pago aprobado
            orden.estado              = 'aprobada'
            orden.codigo_autorizacion = data.get('authorization_code')
            orden.fecha_pago          = timezone.now()
            orden.save()

            orden.prenda.estado = 'vendida'
            orden.prenda.save()

            # Crear envío automáticamente
            from envios.models import Envio
            Envio.objects.get_or_create(
                orden=orden,
                defaults={
                    'estado'   : 'pendiente',
                    'direccion': orden.usuario.direccion or '',
                }
            )

            pay_type  = 'Débito' if data.get('payment_type_code') == 'VD' else 'Crédito'
            monto_fmt = f"${int(data.get('amount', 0)):,}".replace(',', '.')
            fecha     = dt.datetime.strptime(data['transaction_date'], '%Y-%m-%dT%H:%M:%S.%fZ')

            resultado = {
                'estado'              : 'APROBADO',
                'fecha'               : fecha.strftime('%d-%m-%Y %H:%M:%S'),
                'tarjeta'             : data['card_detail']['card_number'],
                'tipo_pago'           : pay_type,
                'monto'               : monto_fmt,
                'codigo_autorizacion' : data['authorization_code'],
                'buy_order'           : data['buy_order'],
                'prenda_nombre'       : orden.prenda.nombre,
            }
        else:
            # ❌ Pago rechazado
            orden.estado = 'rechazada'
            orden.save()
            resultado = {
                'estado'        : 'RECHAZADO',
                'buy_order'     : orden.buy_order,
                'prenda_nombre' : orden.prenda.nombre,
                'mensaje'       : 'El pago fue rechazado. Intenta con otra tarjeta.',
            }
    else:
        resultado = {'estado': 'ERROR', 'mensaje': 'Error al confirmar el pago.'}

    return render(request, 'transacciones/commit-pay.html', {'resultado': resultado})


@login_required
def historial_compras(request):
    ordenes = Orden.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    return render(request, 'transacciones/historial.html', {'ordenes': ordenes})