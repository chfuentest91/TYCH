from django.urls import path
from . import views

urlpatterns = [
    path('',                                  views.lista_conversaciones,  name='lista_conversaciones'),
    path('mis-mensajes/',                     views.mis_conversaciones,    name='mis_conversaciones'),
    path('iniciar/<int:prenda_id>/',          views.iniciar_conversacion,  name='iniciar_conversacion'),
    path('conversacion/<int:conversacion_id>/', views.ver_conversacion,   name='ver_conversacion'),
]