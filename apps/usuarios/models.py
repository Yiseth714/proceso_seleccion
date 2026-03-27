from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('CANDIDATO', 'Candidato'),
    )
    rol = models.CharField(max_length=10, choices=ROLES)
    cedula = models.CharField(max_length=15, blank=True)
    foto = models.ImageField(upload_to='candidatos/', null=True, blank=True)
