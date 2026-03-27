from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Pregunta, IntentoExamen
from django.db.models import Count

def es_candidato(user):
    return user.is_authenticated and user.rol == 'CANDIDATO'

@login_required
@user_passes_test(es_candidato, login_url='login')
def examen(request):
    usuario = request.user

    if IntentoExamen.objects.filter(usuario=usuario).exists():
        resultado = IntentoExamen.objects.get(usuario=usuario)
        return render(request, 'candidato/resultado.html', {
            'puntaje': resultado.puntaje
        })

    # obtener las preguntas
    preguntas = (
        Pregunta.objects.annotate(total_opciones=Count('opciones'))
        .filter(total_opciones=3)
        .order_by('id')
    )[:10]

    if request.method == 'POST':
        respuestas_faltantes = []
        respuestas_invalidas = []

        for pregunta in preguntas:
            opcion_id = request.POST.get(str(pregunta.id))

            if not opcion_id:
                respuestas_faltantes.append(pregunta.id)
                continue

            if not pregunta.opciones.filter(id=opcion_id).exists():
                respuestas_invalidas.append(pregunta.id)

        if respuestas_faltantes or respuestas_invalidas:
            return render(request, 'candidato/examen.html', {
                'preguntas': preguntas,
                'error': 'Debes responder todas las preguntas antes de enviar el examen.'
            })

        puntaje = 0

        for pregunta in preguntas:
            opcion_id = request.POST.get(str(pregunta.id))
            if pregunta.opciones.filter(id=opcion_id, es_correcta=True).exists():
                puntaje += 1

        IntentoExamen.objects.create(
            usuario=usuario,
            puntaje=puntaje
        )

        return render(request, 'candidato/resultado.html', {
            'puntaje': puntaje
        })

    return render(request, 'candidato/examen.html', {
        'preguntas': preguntas
    })
