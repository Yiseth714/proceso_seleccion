from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages

from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.db.models import OuterRef, Subquery
from .forms import CrearUsuarioForm, EditarUsuarioForm
from .models import Usuario
from apps.evaluaciones.models import IntentoExamen

class loginPersonalizado(LoginView):
    template_name = 'auth/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser:
            return '/admin/'  # Django Admin
        elif user.rol == 'ADMIN':
            return '/administrador/dashboard/'
        elif user.rol == 'CANDIDATO':
            return '/candidato/examen/'

        return '/login/'

def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.rol == 'ADMIN')

@method_decorator(user_passes_test(es_admin, login_url='login'), name='dispatch')
class CrearUsuarioView(LoginRequiredMixin, CreateView):
    form_class = CrearUsuarioForm
    template_name = 'administrador/crear_candidato.html'
    success_url = reverse_lazy('crear_usuario')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        password_plano = form.cleaned_data['password1']
        response = super().form_valid(form)

        if self.object.email:
            try:
                send_mail(
                    subject='Tu cuenta ha sido creada',
                    message=(
                        f'Hola {self.object.first_name or self.object.username},\n\n'
                        'Tu cuenta para el sistema de evaluacion fue creada.\n'
                        f'Usuario: {self.object.username}\n'
                        f'Contraseña: {password_plano}\n\n'
                        'Te recomendamos cambiar la contrasña despues de iniciar sesion.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.object.email],
                    fail_silently=False,
                )
            except Exception:
                messages.warning(self.request, 'Usuario creado, pero no se pudo enviar el correo.')
        else:
            messages.warning(self.request, 'El usuario fue creado sin correo electronico.')

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        puntaje_subquery = IntentoExamen.objects.filter(
            usuario=OuterRef('pk')
        ).values('puntaje')[:1]
        context['usuarios'] = Usuario.objects.filter(rol='CANDIDATO').annotate(
            puntaje_examen=Subquery(puntaje_subquery)
        ).order_by('-id')
        return context


@method_decorator(user_passes_test(es_admin, login_url='login'), name='dispatch')
class EditarUsuarioView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = EditarUsuarioForm
    template_name = 'administrador/editar_candidato.html'
    success_url = reverse_lazy('crear_usuario')
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return Usuario.objects.filter(rol='CANDIDATO')


@method_decorator(user_passes_test(es_admin, login_url='login'), name='dispatch')
class EliminarUsuarioView(LoginRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'administrador/eliminar_candidato.html'
    success_url = reverse_lazy('crear_usuario')
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return Usuario.objects.filter(rol='CANDIDATO')

# @login_required
# @user_passes_test(es_admin, login_url='login')
# def dashboard_admin(request):
#     return render(request, 'administrador/dashboard.html')
