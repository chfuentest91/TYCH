from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from catalogo.models import Prenda
from usuarios.models import Usuario


class CalificacionPrenda(models.Model):
    prenda     = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='calificaciones')
    comprador  = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='calificaciones_dadas')
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    creada_en  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comprador.username} → {self.prenda.nombre}: {self.puntuacion}★"

    class Meta:
        verbose_name = 'Calificación de Prenda'
        unique_together = ('prenda', 'comprador')


class CalificacionVendedor(models.Model):
    vendedor   = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='calificaciones_recibidas')
    comprador  = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='calificaciones_vendedor_dadas')
    prenda     = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='calificaciones_vendedor')
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    creada_en  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comprador.username} → {self.vendedor.username}: {self.puntuacion}★"

    class Meta:
        verbose_name = 'Calificación de Vendedor'
        unique_together = ('vendedor', 'comprador', 'prenda')