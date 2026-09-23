from django import forms
from .models import Livro

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ["titulo", "autor", "ano", "disponivel", "tipo_acervo", "categoria"]
        labels = {
            "titulo": "Nome / Título",
            "autor": "Autor",
            "ano": "Ano",
            "disponivel": "Disponível",
            "tipo_acervo": "Tipo de acervo",
            "categoria": "Categoria",
        }
