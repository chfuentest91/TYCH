from django import forms
from .models import Prenda, Categoria

class PrendaForm(forms.ModelForm):
    class Meta:
        model = Prenda
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'talla', 'genero', 'estado', 'imagen']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].label = 'Nombre de la prenda'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['precio'].label = 'Precio ($)'
        self.fields['categoria'].label = 'Categoría'
        self.fields['talla'].label = 'Talla'
        self.fields['genero'].label = 'Género'
        self.fields['estado'].label = 'Estado'
        self.fields['imagen'].label = 'Imagen'
        self.fields['imagen'].required = False

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['nombre'].widget.attrs['placeholder'] = 'Ej: Polera azul manga corta'
        self.fields['precio'].widget.attrs['placeholder'] = 'Ej: 5990'
        self.fields['descripcion'].widget.attrs['rows'] = 3