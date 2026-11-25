"""Métricas do dashboard.

Toda função recebe um queryset base (já filtrado por período) e devolve
dados simples (dict/list), prontos para o template, a API e o CSV.
"""
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from .models import Livro

ROTULOS_CATEGORIA = dict(Livro.CATEGORIAS)


def kpis(base):
    """KPIs: vários totais em uma só consulta (aggregate + Count com filtro)."""
    return base.aggregate(
        total=Count("id"),
        disponiveis=Count("id", filter=Q(disponivel=True)),
        digitais=Count("id", filter=Q(tipo_acervo="DIGITAL")),
        fisicos=Count("id", filter=Q(tipo_acervo="FISICO")),
    )


def ranking_autores(base, limite=5):
    """Ranking: os autores com mais livros no acervo."""
    return list(
        base.values("autor")
        .annotate(total=Count("id"))
        .order_by("-total", "autor")[:limite]
    )


def livros_por_mes(base):
    """Série no tempo: livros cadastrados por mês."""
    qs = (
        base.annotate(mes=TruncMonth("criado_em"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )
    return [{"mes": r["mes"].strftime("%m/%Y"), "total": r["total"]} for r in qs]


def distribuicao_categoria(base):
    """Distribuição: fatias do acervo por categoria (classificação 000–900)."""
    qs = (
        base.values("categoria")
        .annotate(total=Count("id"))
        .order_by("categoria")
    )
    return [
        {
            "categoria": r["categoria"],
            "rotulo": ROTULOS_CATEGORIA.get(r["categoria"], r["categoria"]),
            "total": r["total"],
        }
        for r in qs
    ]


def calcular_metricas(base):
    """Reúne todas as métricas; usada pela view HTML e pela API JSON."""
    return {
        "kpis": kpis(base),
        "ranking": ranking_autores(base),
        "por_mes": livros_por_mes(base),
        "distribuicao": distribuicao_categoria(base),
    }
