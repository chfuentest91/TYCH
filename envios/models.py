from django.db import models
from transacciones.models import Orden
from usuarios.models import Usuario


class Envio(models.Model):
    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente'),
        ('en_camino',  'En camino'),
        ('entregado',  'Entregado'),
    ]

    orden           = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name='envio')
    estado          = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion       = models.CharField(max_length=200, blank=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion  = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Envío #{self.orden.buy_order} — {self.estado}"

    class Meta:
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'