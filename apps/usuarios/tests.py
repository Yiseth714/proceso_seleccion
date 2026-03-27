from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import CrearUsuarioForm, EditarUsuarioForm


class UsuariosTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="admin1",
            password="Passw0rd123",
            rol="ADMIN",
        )
        self.candidato = User.objects.create_user(
            username="candidato1",
            password="Passw0rd123",
            rol="CANDIDATO",
        )

    def _login(self, user):
        self.client.login(username=user.username, password="Passw0rd123")

    def test_dashboard_requiere_login(self):
        response = self.client.get(reverse("crear_usuario"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_dashboard_restringido_a_admin(self):
        self._login(self.candidato)
        response = self.client.get(reverse("crear_usuario"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_admin_puede_acceder_dashboard(self):
        self._login(self.admin)
        response = self.client.get(reverse("crear_usuario"))
        self.assertEqual(response.status_code, 200)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_crear_usuario_envia_correo(self):
        self._login(self.admin)
        data = {
            "username": "nuevo1",
            "first_name": "Nuevo",
            "last_name": "Usuario",
            "email": "nuevo@example.com",
            "cedula": "123",
            "password1": "Passw0rd123",
            "password2": "Passw0rd123",
        }
        response = self.client.post(reverse("crear_usuario"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_form_crear_usuario_passwords_no_coinciden(self):
        data = {
            "username": "x1",
            "first_name": "A",
            "last_name": "B",
            "email": "a@b.com",
            "cedula": "123",
            "password1": "Passw0rd123",
            "password2": "Passw0rd124",
        }
        form = CrearUsuarioForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_crear_usuario_asigna_rol(self):
        data = {
            "username": "x2",
            "first_name": "A",
            "last_name": "B",
            "email": "a2@b.com",
            "cedula": "123",
            "password1": "Passw0rd123",
            "password2": "Passw0rd123",
        }
        form = CrearUsuarioForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.rol, "CANDIDATO")

    def test_form_editar_usuario_requiere_username(self):
        form = EditarUsuarioForm(data={"username": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
