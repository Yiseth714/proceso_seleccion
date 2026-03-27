from django.urls import path
from .views import examen

urlpatterns = [
    path('examen/', examen, name='examen'),
]
