from django.db import models
from catalogo.models import Prenda
from usuarios.models import Usuario


class Carrito(models.Model):
    usuario    = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='carrito')
    creado_en  = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def total(self):
        return sum(item.prenda.precio for item in self.items.all())

    def cantidad_items(self):
        return self.items.count()

    def __str__(self):
        return f"Carrito de {self.usuario.username}"


class ItemCarrito(models.Model):
    carrito    = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    prenda     = models.ForeignKey(Prenda, on_delete=models.CASCADE)
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('carrito', 'prenda')

    def __str__(self):
        return f"{self.prenda.nombre} en carrito de {self.carrito.usuario.username}"


class OpcionDespacho(models.Model):
    TIPO_CHOICES = [
        ('retiro',      'Retiro en tienda'),
        ('chilexpress', 'Chilexpress'),
        ('starken',     'Starken'),
        ('blueexpress', 'BlueExpress'),
    ]
    tipo   = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} — ${self.precio:,}"