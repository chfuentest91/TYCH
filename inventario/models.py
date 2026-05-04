from django.db import models

from django.db import models
from catalogo.models import Prenda
from usuarios.models import Usuario


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    prenda      = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='movimientos')
    tipo        = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=200, blank=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} — {self.prenda.nombre} ({self.fecha:%d/%m/%Y})"

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']