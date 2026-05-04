from django.db import models
from usuarios.models import Usuario

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Prenda(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('vendida', 'Vendida'),
    ]
    TALLA_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
    ]
    GENERO_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('unisex', 'Unisex'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    talla = models.CharField(max_length=5, choices=TALLA_CHOICES)
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, default='unisex')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='disponible')
    imagen = models.ImageField(upload_to='prendas/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.estado}"

    class Meta:
        verbose_name = 'Prenda'
        verbose_name_plural = 'Prendas'