from django.urls import path
from . import views

urlpatterns = [
    path('comprar/<int:prenda_id>/', views.iniciar_pago, name='iniciar-pago'),
    path('commit-pago/',             views.commit_pago,  name='commit-pago'),
]