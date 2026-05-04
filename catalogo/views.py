from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Prenda
from .forms import PrendaForm


def solo_admin(request):
    if request.user.perfil != 'administrador':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return False
    return True


def home(request):
    prendas_destacadas = Prenda.objects.filter(estado='disponible').order_by('-fecha_publicacion')[:6]
    return render(request, 'catalogo/home.html', {'prendas': prendas_destacadas})


def lista_prendas(request):
    from .models import Categoria
    prendas = Prenda.objects.all().order_by('-fecha_publicacion')
    categorias = Categoria.objects.all()

    categoria_id = request.GET.get('categoria')
    talla        = request.GET.get('talla')
    precio_min   = request.GET.get('precio_min')
    precio_max   = request.GET.get('precio_max')
    busqueda     = request.GET.get('busqueda')
    genero       = request.GET.get('genero')

    if categoria_id:
        prendas = prendas.filter(categoria_id=categoria_id)
    if talla:
        prendas = prendas.filter(talla=talla)
    if precio_min:
        prendas = prendas.filter(precio__gte=precio_min)
    if precio_max:
        prendas = prendas.filter(precio__lte=precio_max)
    if busqueda:
        prendas = prendas.filter(nombre__icontains=busqueda)
    if genero:
        prendas = prendas.filter(genero=genero)

    es_admin = request.user.is_authenticated and request.user.perfil == 'administrador'

    return render(request, 'catalogo/lista_prendas.html', {
        'prendas'   : prendas,
        'categorias': categorias,
        'es_admin'  : es_admin,
    })


@login_required(login_url='/usuarios/login/')
def publicar_prenda(request):
    if not solo_admin(request):
        return redirect('lista_prendas')
    if request.method == 'POST':
        form = PrendaForm(request.POST, request.FILES)
        if form.is_valid():
            prenda = form.save(commit=False)
            prenda.admin = request.user
            prenda.save()
            messages.success(request, '¡Prenda publicada exitosamente!')
            return redirect('lista_prendas')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PrendaForm()
    return render(request, 'catalogo/publicar_prenda.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def editar_prenda(request, pk):
    if not solo_admin(request):
        return redirect('lista_prendas')
    prenda = get_object_or_404(Prenda, pk=pk)
    if request.method == 'POST':
        form = PrendaForm(request.POST, request.FILES, instance=prenda)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Prenda actualizada correctamente!')
            return redirect('lista_prendas')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PrendaForm(instance=prenda)
    return render(request, 'catalogo/editar_prenda.html', {'form': form, 'prenda': prenda})


@login_required(login_url='/usuarios/login/')
def eliminar_prenda(request, pk):
    if not solo_admin(request):
        return redirect('lista_prendas')
    prenda = get_object_or_404(Prenda, pk=pk)
    if request.method == 'POST':
        prenda.delete()
        messages.success(request, '¡Prenda eliminada correctamente!')
        return redirect('lista_prendas')
    return render(request, 'catalogo/confirmar_eliminar.html', {'prenda': prenda})


@login_required(login_url='/usuarios/login/')
def cambiar_estado(request, pk):
    if not solo_admin(request):
        return redirect('lista_prendas')
    prenda = get_object_or_404(Prenda, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['disponible', 'reservada', 'vendida']:
            prenda.estado = nuevo_estado
            prenda.save()
            messages.success(request, f'Estado cambiado a {nuevo_estado}.')
        return redirect('lista_prendas')
    return render(request, 'catalogo/cambiar_estado.html', {'prenda': prenda})


def detalle_prenda(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)

    from calificaciones.models import CalificacionPrenda
    from transacciones.models import Orden

    calificaciones = CalificacionPrenda.objects.filter(
        prenda=prenda
    ).select_related('comprador').order_by('-creada_en')

    puede_calificar = False
    if request.user.is_authenticated and request.user.perfil != 'administrador':
        compro = Orden.objects.filter(
            usuario=request.user, prenda=prenda, estado='aprobada'
        ).exists()
        ya_califico = CalificacionPrenda.objects.filter(
            prenda=prenda, comprador=request.user
        ).exists()
        puede_calificar = compro and not ya_califico

    es_admin = request.user.is_authenticated and request.user.perfil == 'administrador'

    return render(request, 'catalogo/detalle_prenda.html', {
        'prenda'         : prenda,
        'calificaciones' : calificaciones,
        'puede_calificar': puede_calificar,
        'es_admin'       : es_admin,
    })