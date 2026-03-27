from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.urls import include, path
from apps.usuarios.views import loginPersonalizado

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginPersonalizado.as_view(), name='home'),
    path('login/', loginPersonalizado.as_view(), name='login'),
    path('logout/', DjangoLogoutView.as_view(next_page='login'), name='logout'),
    path('candidato/', include('apps.evaluaciones.urls')),
    path('administrador/', include('apps.usuarios.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
