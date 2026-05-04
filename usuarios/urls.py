from django.urls import path
from . import views

urlpatterns = [
    path('registro/',              views.registro,          name='registro'),
    path('login/',                 views.login_view,        name='login'),
    path('logout/',                views.logout_view,       name='logout'),
    path('perfil/',                views.editar_perfil,     name='editar_perfil'),
    path('gestion/',               views.gestion_usuarios,  name='gestion_usuarios'),
    path('eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
]