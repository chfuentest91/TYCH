from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Prenda
from .forms import PrendaForm


@login_required(login_url='/usuarios/login/')
def lista_prendas(request):
    prendas = Prenda.objects.all().order_by('-fecha_publicacion')
    return render(request, 'catalogo/lista_prendas.html', {'prendas': prendas})


@login_required(login_url='/usuarios/login/')
def publicar_prenda(request):
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
    prenda = get_object_or_404(Prenda, pk=pk)
    if request.method == 'POST':
        prenda.delete()
        messages.success(request, '¡Prenda eliminada correctamente!')
        return redirect('lista_prendas')
    return render(request, 'catalogo/confirmar_eliminar.html', {'prenda': prenda})


@login_required(login_url='/usuarios/login/')
def cambiar_estado(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['disponible', 'reservada', 'vendida']:
            prenda.estado = nuevo_estado
            prenda.save()
            messages.success(request, f'Estado cambiado a {nuevo_estado}.')
        return redirect('lista_prendas')
    return render(request, 'catalogo/cambiar_estado.html', {'prenda': prenda})