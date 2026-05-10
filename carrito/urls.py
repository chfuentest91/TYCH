from django.urls import path
from . import views

urlpatterns = [
    path('',                  views.ver_carrito,          name='ver_carrito'),
    path('agregar/<int:prenda_id>/', views.agregar_item,  name='agregar_item'),
    path('eliminar/<int:item_id>/',  views.eliminar_item, name='eliminar_item'),
    path('despacho/',         views.seleccionar_despacho, name='seleccionar_despacho'),
    path('pagar/',            views.iniciar_pago_carrito,  name='pagar_carrito'),
    path('commit-pago/',      views.commit_pago_carrito,   name='commit_pago_carrito'),
]