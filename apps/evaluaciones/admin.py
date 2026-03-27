from django.contrib import admin
from django.forms import BaseInlineFormSet
from .models import Pregunta, Opcion

class OpcionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        opciones = 0
        correctas = 0

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                opciones += 1
                if form.cleaned_data.get('es_correcta'):
                    correctas += 1

        if opciones != 3:
            raise ValueError("Cada pregunta debe tener exactamente 3 opciones.")

        if correctas != 1:
            raise ValueError("Debe existir una única opción correcta.")

class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 3
    max_num = 3
    formset = OpcionInlineFormSet

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('texto',)
    inlines = [OpcionInline]
