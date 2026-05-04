from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display  = ['username', 'email', 'perfil', 'rut', 'telefono', 'date_joined']
    list_filter   = ['perfil']
    search_fields = ['username', 'email', 'rut']