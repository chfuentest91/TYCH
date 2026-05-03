from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('administrador', 'Administrador'),
        ('cliente', 'Cliente'),
    ]
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='cliente')
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    rut = models.CharField(max_length=12, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.perfil}"