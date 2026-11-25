import csv

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .dashboard import calcular_metricas
from .forms import LivroForm, PeriodoForm, filtrar_periodo
from .models import Livro

def lista_livros(request):
    livros = Livro.objects.all().order_by("titulo")
    nome = request.GET.get("nome", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    if nome:
        livros = livros.filter(titulo__icontains=nome)
    if tipo:
        livros = livros.filter(tipo_acervo=tipo)
    if categoria:
        livros = livros.filter(categoria=categoria)

    return render(request, "acervo/lista.html", {
        "livros": livros,
        "nome": nome,
        "tipo": tipo,
        "categoria": categoria,
        "tipos": Livro.TIPOS_ACERVO,
        "categorias": Livro.CATEGORIAS,
    })

def novo_livro(request):
    if request.method == "POST":
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = LivroForm()
    return render(request, "acervo/form.html", {"form": form})


# ---------------------------------------------------------------------------
# Dashboard e relatórios (Aula 17)
# ---------------------------------------------------------------------------

def _base_filtrada(request):
    """Uma base filtrada por período: todas as métricas e o CSV derivam dela."""
    form = PeriodoForm(request.GET)
    return form, filtrar_periodo(form, Livro.objects.all())


def dashboard(request):
    form, base = _base_filtrada(request)
    contexto = calcular_metricas(base)
    contexto["form"] = form
    contexto["querystring"] = request.GET.urlencode()
    return render(request, "acervo/dashboard.html", contexto)


def dashboard_api(request):
    """Mesmas métricas do dashboard em JSON, para outros clientes."""
    _, base = _base_filtrada(request)
    return JsonResponse(calcular_metricas(base))


def _celula_segura(valor):
    """Evita que o Excel trate texto como fórmula (células com = + - @)."""
    texto = str(valor)
    if texto and texto[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + texto
    return texto


def exportar_csv(request):
    _, base = _base_filtrada(request)
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="livros.csv"'
    resp.write("\ufeff")  # BOM: o Excel abre os acentos corretamente
    w = csv.writer(resp)
    w.writerow(["Título", "Autor", "Ano", "Tipo de acervo", "Categoria",
                "Disponível", "Cadastrado em"])
    for livro in base.order_by("titulo"):
        w.writerow([
            _celula_segura(livro.titulo),
            _celula_segura(livro.autor),
            livro.ano,
            livro.get_tipo_acervo_display(),
            livro.get_categoria_display(),
            "Sim" if livro.disponivel else "Não",
            timezone.localtime(livro.criado_em).strftime("%d/%m/%Y %H:%M"),
        ])
    return resp
