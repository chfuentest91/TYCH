from django.db import models
from usuarios.models import Usuario
from catalogo.models import Prenda


class Conversacion(models.Model):
    prenda    = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='conversaciones')
    cliente   = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='conversaciones_cliente')
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversación: {self.cliente.username} — {self.prenda.nombre}"

    class Meta:
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        unique_together = ('prenda', 'cliente')


class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    remitente    = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados')
    contenido    = models.TextField()
    enviado_en   = models.DateTimeField(auto_now_add=True)
    leido        = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.remitente.username}: {self.contenido[:40]}"

    class Meta:
        ordering = ['enviado_en']