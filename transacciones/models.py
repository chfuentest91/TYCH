from django.db import models
from catalogo.models import Prenda
from usuarios.models import Usuario


class Orden(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    prenda               = models.ForeignKey(Prenda, on_delete=models.CASCADE)
    usuario              = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    buy_order            = models.CharField(max_length=50, unique=True)
    monto                = models.IntegerField()
    estado               = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    token_ws             = models.CharField(max_length=200, blank=True, null=True)
    codigo_autorizacion  = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    fecha_pago           = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Orden {self.buy_order} - {self.estado}"

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'