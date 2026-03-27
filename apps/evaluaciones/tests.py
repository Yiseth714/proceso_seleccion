from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Pregunta, Opcion, IntentoExamen


class EvaluacionesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.candidato = User.objects.create_user(
            username="candidato1",
            password="Passw0rd123",
            rol="CANDIDATO",
        )
        self.admin = User.objects.create_user(
            username="admin1",
            password="Passw0rd123",
            rol="ADMIN",
        )

        self.preguntas = []
        for i in range(10):
            pregunta = Pregunta.objects.create(texto=f"Pregunta {i + 1}")
            Opcion.objects.create(pregunta=pregunta, texto="A", es_correcta=True)
            Opcion.objects.create(pregunta=pregunta, texto="B", es_correcta=False)
            Opcion.objects.create(pregunta=pregunta, texto="C", es_correcta=False)
            self.preguntas.append(pregunta)

    def _login(self, user):
        self.client.login(username=user.username, password="Passw0rd123")

    def _build_respuestas(self, correctas=True):
        data = {}
        for pregunta in self.preguntas:
            if correctas:
                opcion = pregunta.opciones.filter(es_correcta=True).first()
            else:
                opcion = pregunta.opciones.filter(es_correcta=False).first()
            data[str(pregunta.id)] = str(opcion.id)
        return data

    def test_examen_requiere_login(self):
        response = self.client.get(reverse("examen"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_examen_restringido_a_candidato(self):
        self._login(self.admin)
        response = self.client.get(reverse("examen"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_examen_get_muestra_preguntas(self):
        self._login(self.candidato)
        response = self.client.get(reverse("examen"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["preguntas"]), 10)

    def test_examen_post_falta_respuestas(self):
        self._login(self.candidato)
        data = self._build_respuestas()
        data.pop(str(self.preguntas[0].id))
        response = self.client.post(reverse("examen"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context)
        self.assertFalse(IntentoExamen.objects.filter(usuario=self.candidato).exists())

    def test_examen_post_respuesta_invalida(self):
        self._login(self.candidato)
        data = self._build_respuestas()
        data[str(self.preguntas[0].id)] = "999999"
        response = self.client.post(reverse("examen"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context)
        self.assertFalse(IntentoExamen.objects.filter(usuario=self.candidato).exists())

    def test_examen_post_calcula_puntaje(self):
        self._login(self.candidato)
        data = self._build_respuestas(correctas=True)
        response = self.client.post(reverse("examen"), data)
        self.assertEqual(response.status_code, 200)
        intento = IntentoExamen.objects.get(usuario=self.candidato)
        self.assertEqual(intento.puntaje, 10)
        self.assertEqual(response.context["puntaje"], 10)

    def test_examen_no_permite_reintento(self):
        self._login(self.candidato)
        data = self._build_respuestas(correctas=True)
        self.client.post(reverse("examen"), data)
        response = self.client.get(reverse("examen"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("puntaje", response.context)
