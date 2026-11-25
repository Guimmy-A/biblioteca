import csv
import io
from datetime import datetime

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from .dashboard import (
    distribuicao_categoria,
    kpis,
    livros_por_mes,
    ranking_autores,
)
from .models import Livro


def data(ano, mes, dia):
    """Meio-dia no fuso do projeto, longe da virada do dia."""
    return timezone.make_aware(datetime(ano, mes, dia, 12, 0))


class DadosConhecidosMixin:
    """Números fáceis de conferir à mão (nunca valores aleatórios).

    5 livros | 3 disponíveis | 3 digitais | 2 físicos
    Cadastros: ago/2026 = 2, set/2026 = 1, out/2026 = 2
    Autores: Machado de Assis = 2, os demais = 1
    Categorias: 600 = 2, 800 = 3
    """

    def setUp(self):
        dados = [
            ("Dom Casmurro", "Machado de Assis", 1899, True, "DIGITAL", "800", data(2026, 8, 10)),
            ("Memórias Póstumas", "Machado de Assis", 1881, True, "FISICO", "800", data(2026, 8, 20)),
            ("O Guarani", "José de Alencar", 1857, False, "FISICO", "800", data(2026, 9, 5)),
            ("Algoritmos", "Thomas Cormen", 2009, True, "DIGITAL", "600", data(2026, 10, 1)),
            ("Código Limpo", "Robert Martin", 2008, False, "DIGITAL", "600", data(2026, 10, 15)),
        ]
        for titulo, autor, ano, disp, tipo, cat, criado in dados:
            livro = Livro.objects.create(
                titulo=titulo, autor=autor, ano=ano,
                disponivel=disp, tipo_acervo=tipo, categoria=cat,
            )
            # criado_em não é editável: ajusta direto no banco.
            Livro.objects.filter(pk=livro.pk).update(criado_em=criado)


class MetricasTest(DadosConhecidosMixin, TestCase):
    def test_kpis(self):
        self.assertEqual(kpis(Livro.objects.all()), {
            "total": 5, "disponiveis": 3, "digitais": 3, "fisicos": 2,
        })

    def test_ranking_ordenado_e_com_desempate_por_nome(self):
        ranking = ranking_autores(Livro.objects.all())
        self.assertEqual(ranking[0], {"autor": "Machado de Assis", "total": 2})
        self.assertEqual(
            [r["autor"] for r in ranking[1:]],
            ["José de Alencar", "Robert Martin", "Thomas Cormen"],
        )

    def test_ranking_respeita_o_limite(self):
        self.assertEqual(len(ranking_autores(Livro.objects.all(), limite=2)), 2)

    def test_serie_por_mes_em_ordem_cronologica(self):
        self.assertEqual(livros_por_mes(Livro.objects.all()), [
            {"mes": "08/2026", "total": 2},
            {"mes": "09/2026", "total": 1},
            {"mes": "10/2026", "total": 2},
        ])

    def test_distribuicao_por_categoria(self):
        dist = distribuicao_categoria(Livro.objects.all())
        self.assertEqual([(d["categoria"], d["total"]) for d in dist],
                         [("600", 2), ("800", 3)])
        self.assertIn("Literatura", dist[1]["rotulo"])

    def test_soma_da_serie_confere_com_o_kpi_total(self):
        base = Livro.objects.all()
        soma = sum(item["total"] for item in livros_por_mes(base))
        self.assertEqual(soma, kpis(base)["total"])


class DashboardViewTest(DadosConhecidosMixin, TestCase):
    def test_dashboard_sem_filtro(self):
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["kpis"]["total"], 5)

    def test_filtro_por_periodo(self):
        r = self.client.get(reverse("dashboard"), {"inicio": "2026-08-01", "fim": "2026-09-30"})
        self.assertEqual(r.context["kpis"]["total"], 3)
        self.assertEqual([m["mes"] for m in r.context["por_mes"]], ["08/2026", "09/2026"])

    def test_filtro_so_com_inicio(self):
        r = self.client.get(reverse("dashboard"), {"inicio": "2026-10-01"})
        self.assertEqual(r.context["kpis"]["total"], 2)

    def test_filtro_inclui_o_dia_inicial_e_o_final(self):
        r = self.client.get(reverse("dashboard"), {"inicio": "2026-08-10", "fim": "2026-08-10"})
        self.assertEqual(r.context["kpis"]["total"], 1)

    def test_data_invalida_nao_gera_erro_500(self):
        r = self.client.get(reverse("dashboard"), {"inicio": "abc"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context["form"].errors)
        self.assertEqual(r.context["kpis"]["total"], 5)  # filtro não aplicado

    def test_inicio_maior_que_fim_nao_filtra_e_mostra_erro(self):
        r = self.client.get(reverse("dashboard"), {"inicio": "2026-10-01", "fim": "2026-08-01"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context["form"].non_field_errors())
        self.assertEqual(r.context["kpis"]["total"], 5)

    def test_periodo_sem_dados_nao_quebra(self):
        r = self.client.get(reverse("dashboard"), {"inicio": "2030-01-01"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["kpis"]["total"], 0)
        self.assertEqual(r.context["ranking"], [])
        self.assertContains(r, "Sem dados no período.")

    def test_dashboard_sem_nenhum_livro(self):
        Livro.objects.all().delete()
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["kpis"]["total"], 0)

    def test_numero_fixo_de_consultas(self):
        """Uma consulta por métrica (4), sem N+1."""
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("dashboard"))
        self.assertLessEqual(len(ctx), 4)


class ExportacaoTest(DadosConhecidosMixin, TestCase):
    def _linhas(self, resposta):
        texto = resposta.content.decode("utf-8-sig")
        return list(csv.reader(io.StringIO(texto)))

    def test_csv_com_todos_os_livros(self):
        r = self.client.get(reverse("exportar_csv"))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r["Content-Type"].startswith("text/csv"))
        self.assertIn("attachment", r["Content-Disposition"])
        linhas = self._linhas(r)
        self.assertEqual(linhas[0][0], "Título")
        self.assertEqual(len(linhas) - 1, 5)

    def test_csv_usa_a_mesma_base_filtrada_do_dashboard(self):
        r = self.client.get(reverse("exportar_csv"), {"inicio": "2026-10-01"})
        linhas = self._linhas(r)
        self.assertEqual(len(linhas) - 1, 2)
        self.assertEqual({l[0] for l in linhas[1:]}, {"Algoritmos", "Código Limpo"})

    def test_csv_neutraliza_formulas(self):
        Livro.objects.create(
            titulo="=HYPERLINK(\"http://exemplo.com\")", autor="@alguem", ano=2020,
            tipo_acervo="DIGITAL", categoria="000",
        )
        linhas = self._linhas(self.client.get(reverse("exportar_csv")))
        titulos = [l[0] for l in linhas[1:]]
        autores = [l[1] for l in linhas[1:]]
        self.assertFalse(any(t.startswith("=") for t in titulos))
        self.assertIn("'@alguem", autores)


class ApiTest(DadosConhecidosMixin, TestCase):
    def test_api_devolve_as_metricas_em_json(self):
        r = self.client.get(reverse("dashboard_api"))
        self.assertEqual(r.status_code, 200)
        corpo = r.json()
        self.assertEqual(corpo["kpis"]["total"], 5)
        self.assertEqual(corpo["ranking"][0]["autor"], "Machado de Assis")

    def test_api_respeita_o_periodo(self):
        r = self.client.get(reverse("dashboard_api"), {"fim": "2026-08-31"})
        self.assertEqual(r.json()["kpis"]["total"], 2)
