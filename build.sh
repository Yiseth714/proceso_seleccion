#!/usr/bin/env bash
# Salir inmediatamente si un comando falla
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Recopilar archivos estáticos (CSS, JS, Imágenes del admin)
python manage.py collectstatic --no-input

# 3. Aplicar migraciones a la base de datos de Railway
python manage.py migrate

# 4. (Opcional) Crear superusuario automáticamente si no existe
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('sergio', 'yisethvaleguti@.com', 'olivia123')"