from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_prendas, name='lista_prendas'),
    path('publicar/', views.publicar_prenda, name='publicar_prenda'),
    path('editar/<int:pk>/', views.editar_prenda, name='editar_prenda'),
    path('eliminar/<int:pk>/', views.eliminar_prenda, name='eliminar_prenda'),
    path('estado/<int:pk>/', views.cambiar_estado, name='cambiar_estado'),
]