from django.shortcuts import render


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from catalogo.models import Prenda, Categoria
from .models import MovimientoInventario


@login_required
def panel_inventario(request):
    if request.user.perfil != 'administrador':
        return render(request, 'inventario/sin_acceso.html')

    # Filtros
    categoria_id = request.GET.get('categoria')
    estado       = request.GET.get('estado')

    prendas = Prenda.objects.select_related('categoria').all()
    if categoria_id:
        prendas = prendas.filter(categoria__id=categoria_id)
    if estado:
        prendas = prendas.filter(estado=estado)

    # Estadísticas
    total        = Prenda.objects.count()
    disponibles  = Prenda.objects.filter(estado='disponible').count()
    vendidas     = Prenda.objects.filter(estado='vendida').count()
    reservadas   = Prenda.objects.filter(estado='reservada').count()

    # Últimos movimientos
    movimientos = MovimientoInventario.objects.select_related('prenda', 'registrado_por')[:10]

    categorias = Categoria.objects.all()

    context = {
        'prendas'     : prendas,
        'categorias'  : categorias,
        'movimientos' : movimientos,
        'total'       : total,
        'disponibles' : disponibles,
        'vendidas'    : vendidas,
        'reservadas'  : reservadas,
    }
    return render(request, 'inventario/panel.html', context)