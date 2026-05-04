from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.lista_envios,     name='lista_envios'),
    path('actualizar/<int:envio_id>/', views.actualizar_estado, name='actualizar_envio'),
    path('mis-envios/',            views.mis_envios,       name='mis_envios'),
]