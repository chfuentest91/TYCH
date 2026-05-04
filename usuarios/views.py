from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm, EditarPerfilForm
from .models import Usuario


def registro(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, '¡Registro exitoso! Bienvenido a TYCH.')
            return redirect(next_url)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form, 'next': next_url})


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            messages.success(request, f'¡Bienvenido {usuario.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'usuarios/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@login_required(login_url='/usuarios/login/')
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado correctamente!')
            return redirect('editar_perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def gestion_usuarios(request):
    if request.user.perfil != 'administrador':
        return redirect('home')
    clientes = Usuario.objects.filter(perfil='cliente').order_by('-date_joined')
    return render(request, 'usuarios/gestion_usuarios.html', {'clientes': clientes})


@login_required(login_url='/usuarios/login/')
def eliminar_usuario(request, user_id):
    if request.user.perfil != 'administrador':
        return redirect('home')
    usuario = get_object_or_404(Usuario, id=user_id, perfil='cliente')
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f'Usuario {usuario.username} eliminado.')
    return redirect('gestion_usuarios')


@login_required(login_url='/usuarios/login/')
def editar_usuario(request, user_id):
    if request.user.perfil != 'administrador':
        return redirect('home')
    cliente = get_object_or_404(Usuario, id=user_id, perfil='cliente')
    if request.method == 'POST':
        cliente.first_name = request.POST.get('first_name', '')
        cliente.last_name  = request.POST.get('last_name', '')
        cliente.email      = request.POST.get('email', '')
        cliente.rut        = request.POST.get('rut', '')
        cliente.telefono   = request.POST.get('telefono', '')
        cliente.direccion  = request.POST.get('direccion', '')
        cliente.save()
        messages.success(request, f'Usuario {cliente.username} actualizado.')
        return redirect('gestion_usuarios')
    return render(request, 'usuarios/editar_usuario.html', {'cliente': cliente})