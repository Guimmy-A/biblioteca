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


class PeriodoForm(forms.Form):
    """Filtro de período do dashboard (datas de cadastro do livro).

    Valida e converte as datas vindas da URL: um texto como "abc" vira erro
    de formulário em vez de erro 500.
    """
    inicio = forms.DateField(
        required=False,
        label="Início",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    fim = forms.DateField(
        required=False,
        label="Fim",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get("inicio"), dados.get("fim")
        if inicio and fim and inicio > fim:
            raise forms.ValidationError("A data inicial não pode ser maior que a final.")
        return dados


def filtrar_periodo(form, qs):
    """Aplica o período já validado ao queryset; formulário inválido não filtra."""
    if form.is_valid():
        if form.cleaned_data["inicio"]:
            qs = qs.filter(criado_em__date__gte=form.cleaned_data["inicio"])
        if form.cleaned_data["fim"]:
            qs = qs.filter(criado_em__date__lte=form.cleaned_data["fim"])
    return qs
