from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from catalogo.models import Prenda, Categoria
from transacciones.models import Orden
from .models import MovimientoInventario


@login_required
def panel_inventario(request):
    if request.user.perfil != 'administrador':
        return render(request, 'inventario/sin_acceso.html')

    categoria_id = request.GET.get('categoria')
    estado       = request.GET.get('estado')

    prendas = Prenda.objects.select_related('categoria').all()
    if categoria_id:
        prendas = prendas.filter(categoria__id=categoria_id)
    if estado:
        prendas = prendas.filter(estado=estado)

    # Enriquecer cada prenda con datos de su venta
    ordenes_aprobadas = Orden.objects.filter(
        estado='aprobada'
    ).select_related('usuario', 'prenda')
    ventas_por_prenda = {o.prenda_id: o for o in ordenes_aprobadas}

    prendas_con_venta = []
    for prenda in prendas:
        prendas_con_venta.append({
            'prenda' : prenda,
            'orden'  : ventas_por_prenda.get(prenda.id),
        })

    total       = Prenda.objects.count()
    disponibles = Prenda.objects.filter(estado='disponible').count()
    vendidas    = Prenda.objects.filter(estado='vendida').count()
    reservadas  = Prenda.objects.filter(estado='reservada').count()

    movimientos = MovimientoInventario.objects.select_related('prenda', 'registrado_por')[:10]
    categorias  = Categoria.objects.all()

    context = {
        'prendas_con_venta': prendas_con_venta,
        'categorias'       : categorias,
        'movimientos'      : movimientos,
        'total'            : total,
        'disponibles'      : disponibles,
        'vendidas'         : vendidas,
        'reservadas'       : reservadas,
    }
    return render(request, 'inventario/panel.html', context)