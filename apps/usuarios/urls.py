from django.urls import path
from .views import CrearUsuarioView, EditarUsuarioView, EliminarUsuarioView

urlpatterns = [
    path('dashboard/', CrearUsuarioView.as_view(), name='crear_usuario'),
    path('editar/<int:pk>/', EditarUsuarioView.as_view(), name='editar_usuario'),
    path('eliminar/<int:pk>/', EliminarUsuarioView.as_view(), name='eliminar_usuario'),
]
