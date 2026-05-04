from django.urls import path
from . import views

urlpatterns = [
    path('',          views.panel_inventario,    name='inventario'),
    path('panel/',    views.panel_inventario,    name='panel_inventario'),
    path('reportes/', views.reportes_inventario, name='reportes_inventario'),
]