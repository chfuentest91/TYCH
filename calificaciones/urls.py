from django.urls import path
from . import views

urlpatterns = [
    path('prenda/<int:prenda_id>/',   views.calificar_prenda,   name='calificar_prenda'),
    path('vendedor/<int:prenda_id>/', views.calificar_vendedor, name='calificar_vendedor'),
]