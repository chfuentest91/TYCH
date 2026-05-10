from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from catalogo.models import Prenda
from transacciones.models import Orden
from tych import transbank_service
from .models import Carrito, ItemCarrito, OpcionDespacho
import datetime as dt

# ── Tarifas por región ──────────────────────────────────────────────
REGIONES = [
    "Región Metropolitana",
    "Valparaíso",
    "O'Higgins",
    "Maule",
    "Biobío",
    "Araucanía",
    "Los Lagos",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Tarapacá",
    "Arica y Parinacota",
    "Los Ríos",
    "Aysén",
    "Magallanes",
]

TARIFAS = {
    'retiro': {r: 0 for r in REGIONES},
    'chilexpress': {
        "Región Metropolitana": 3990,
        "Valparaíso":           4490,
        "O'Higgins":            4490,
        "Maule":                4990,
        "Biobío":               4990,
        "Araucanía":            5490,
        "Los Lagos":            5990,
        "Antofagasta":          5490,
        "Atacama":              5490,
        "Coquimbo":             4990,
        "Tarapacá":             5990,
        "Arica y Parinacota":   6490,
        "Los Ríos":             5990,
        "Aysén":                7490,
        "Magallanes":           7990,
    },
    'starken': {
        "Región Metropolitana": 3500,
        "Valparaíso":           3990,
        "O'Higgins":            3990,
        "Maule":                4490,
        "Biobío":               4490,
        "Araucanía":            4990,
        "Los Lagos":            5490,
        "Antofagasta":          4990,
        "Atacama":              4990,
        "Coquimbo":             4490,
        "Tarapacá":             5490,
        "Arica y Parinacota":   5990,
        "Los Ríos":             5490,
        "Aysén":                6990,
        "Magallanes":           7490,
    },
    'blueexpress': {
        "Región Metropolitana": 3200,
        "Valparaíso":           3690,
        "O'Higgins":            3690,
        "Maule":                4190,
        "Biobío":               4190,
        "Araucanía":            4690,
        "Los Lagos":            5190,
        "Antofagasta":          4690,
        "Atacama":              4690,
        "Coquimbo":             4190,
        "Tarapacá":             5190,
        "Arica y Parinacota":   5690,
        "Los Ríos":             5190,
        "Aysén":                6690,
        "Magallanes":           6990,
    },
}


def _get_or_create_carrito(usuario):
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    return carrito


@login_required
def ver_carrito(request):
    carrito     = _get_or_create_carrito(request.user)
    items       = carrito.items.select_related('prenda').all()
    opciones    = OpcionDespacho.objects.filter(activo=True)

    despacho_info = request.session.get('despacho_info')
    costo_despacho = 0
    if despacho_info:
        costo_despacho = despacho_info.get('precio', 0)

    total_prendas = carrito.total()
    total_final   = int(total_prendas) + costo_despacho

    return render(request, 'carrito/carrito.html', {
        'carrito'        : carrito,
        'items'          : items,
        'despacho_info'  : despacho_info,
        'total_prendas'  : total_prendas,
        'costo_despacho' : costo_despacho,
        'total_final'    : total_final,
    })


@login_required
def agregar_item(request, prenda_id):
    prenda  = get_object_or_404(Prenda, id=prenda_id, estado='disponible')
    carrito = _get_or_create_carrito(request.user)

    if ItemCarrito.objects.filter(prenda=prenda).exclude(carrito=carrito).exists():
        messages.warning(request, f'"{prenda.nombre}" ya está reservada por otro cliente.')
        return redirect(f'/catalogo/detalle/{prenda_id}/')

    _, created = ItemCarrito.objects.get_or_create(carrito=carrito, prenda=prenda)
    if created:
        prenda.estado = 'reservada'
        prenda.save()
        messages.success(request, f'"{prenda.nombre}" agregada al carrito.')
    else:
        messages.info(request, f'"{prenda.nombre}" ya está en tu carrito.')

    return redirect('/carrito/')


@login_required
def eliminar_item(request, item_id):
    item   = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    prenda = item.prenda
    item.delete()
    prenda.estado = 'disponible'
    prenda.save()
    messages.success(request, f'"{prenda.nombre}" eliminada del carrito.')
    return redirect('/carrito/')


@login_required
def seleccionar_despacho(request):
    opciones = OpcionDespacho.objects.filter(activo=True)

    if request.method == 'POST':
        tipo      = request.POST.get('tipo')
        region    = request.POST.get('region')
        direccion = request.POST.get('direccion', '').strip()

        if not tipo or not region or not direccion:
            messages.error(request, 'Debes completar todos los campos.')
            return render(request, 'carrito/despacho.html', {
                'opciones': opciones,
                'regiones': REGIONES,
                'tarifas' : TARIFAS,
            })

        precio = TARIFAS.get(tipo, {}).get(region, 0)
        opcion = OpcionDespacho.objects.filter(tipo=tipo).first()

        request.session['despacho_info'] = {
            'tipo'     : tipo,
            'nombre'   : opcion.nombre if opcion else tipo,
            'region'   : region,
            'direccion': direccion,
            'precio'   : precio,
        }
        messages.success(request, f'Despacho seleccionado: {opcion.nombre if opcion else tipo} a {region}.')
        return redirect('/carrito/')

    return render(request, 'carrito/despacho.html', {
        'opciones': opciones,
        'regiones': REGIONES,
        'tarifas' : TARIFAS,
        'despacho_info': request.session.get('despacho_info'),
    })


@login_required
def iniciar_pago_carrito(request):
    carrito = _get_or_create_carrito(request.user)
    items   = carrito.items.select_related('prenda').all()

    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('/carrito/')

    despacho_info  = request.session.get('despacho_info')
    costo_despacho = despacho_info.get('precio', 0) if despacho_info else 0
    direccion      = despacho_info.get('direccion', '') if despacho_info else ''

    total      = int(carrito.total()) + costo_despacho
    buy_order  = f"TYCH-CART-{request.user.id}-{int(timezone.now().timestamp())}"
    session_id = str(request.user.id)
    return_url = request.build_absolute_uri('/carrito/commit-pago/')

    response = transbank_service.crear_transaccion(
        buy_order=buy_order,
        session_id=session_id,
        amount=total,
        return_url=return_url,
    )

    if response.status_code == 200:
        tb_data = response.json()
        for item in items:
            Orden.objects.create(
                prenda    = item.prenda,
                usuario   = request.user,
                buy_order = f"{buy_order}-{item.prenda.id}",
                monto     = int(item.prenda.precio),
                token_ws  = tb_data['token'],
                estado    = 'pendiente',
            )
        request.session['carrito_token']     = tb_data['token']
        request.session['carrito_buy_order'] = buy_order
        request.session['carrito_direccion'] = direccion

        return render(request, 'transacciones/send-pay.html', {
            'transbank': tb_data,
            'amount'   : total,
        })
    else:
        messages.error(request, 'No se pudo iniciar el pago. Intenta nuevamente.')
        return redirect('/carrito/')


@login_required
def commit_pago_carrito(request):
    token_ws = request.GET.get('token_ws') or request.POST.get('token_ws')

    if not token_ws:
        return render(request, 'transacciones/commit-pay.html', {
            'resultado': {'estado': 'CANCELADO', 'mensaje': 'El pago fue cancelado.'}
        })

    ordenes = Orden.objects.filter(token_ws=token_ws, usuario=request.user)
    if not ordenes.exists():
        return render(request, 'transacciones/commit-pay.html', {
            'resultado': {'estado': 'ERROR', 'mensaje': 'Órdenes no encontradas.'}
        })

    response = transbank_service.confirmar_transaccion(token_ws)

    if response.status_code == 200:
        data          = response.json()
        status        = data.get('status')
        response_code = data.get('response_code')

        if status == 'AUTHORIZED' and response_code == 0:
            direccion = request.session.get('carrito_direccion', '')

            for orden in ordenes:
                orden.estado              = 'aprobada'
                orden.codigo_autorizacion = data.get('authorization_code')
                orden.fecha_pago          = timezone.now()
                orden.save()
                orden.prenda.estado = 'vendida'
                orden.prenda.save()

                from envios.models import Envio
                Envio.objects.get_or_create(
                    orden=orden,
                    defaults={
                        'estado'   : 'pendiente',
                        'direccion': direccion or orden.usuario.direccion or '',
                    }
                )

            carrito = _get_or_create_carrito(request.user)
            carrito.items.all().delete()
            request.session.pop('despacho_info', None)
            request.session.pop('carrito_token', None)
            request.session.pop('carrito_direccion', None)

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
                'prendas'             : [o.prenda.nombre for o in ordenes],
            }
        else:
            for orden in ordenes:
                orden.estado = 'rechazada'
                orden.save()
                orden.prenda.estado = 'disponible'
                orden.prenda.save()
            resultado = {
                'estado' : 'RECHAZADO',
                'mensaje': 'El pago fue rechazado. Intenta con otra tarjeta.',
            }
    else:
        resultado = {'estado': 'ERROR', 'mensaje': 'Error al confirmar el pago.'}

    return render(request, 'transacciones/commit-pay.html', {'resultado': resultado})