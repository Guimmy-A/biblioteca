# Biblioteca — Acervo Bibliográfico com Dashboard (Aulas 04, 05 e 17 / P2)

Projeto Django de acervo bibliográfico. Nas Aulas 04 e 05 foi criado o cadastro
e a pesquisa de livros; na Aula 17 (P2) foi adicionado um **dashboard com
relatórios**: métricas calculadas pelo ORM, filtro por período, gráficos,
exportação em CSV e API JSON.

## Tecnologias
- Python 3 e Django 5 (`Django>=5.0,<6.0`)
- SQLite (banco local, sem configuração)
- HTML com herança de templates e CSS puro
- Chart.js 4 (carregado por CDN) para os gráficos

## Funcionalidades

### Acervo (Aulas 04 e 05)
- Cadastro de livros (título, autor, ano, disponibilidade)
- Tipo de acervo: Digital ou Físico
- Categoria por classificação 000 a 900
- Pesquisa por nome/título, tipo de acervo e categoria
- Django Admin
- Views, URLs, templates e `ModelForm`
- Layout com herança de templates

### Dashboard e relatórios (Aula 17 / P2)
- **KPIs:** total de livros, disponíveis, digitais e físicos, calculados em uma
  única consulta (`aggregate` + `Count` com `filter=Q(...)`)
- **Ranking:** os 5 autores com mais livros (`values` + `annotate` + `order_by`)
- **Série no tempo:** livros cadastrados por mês (`TruncMonth`), em gráfico de barras
- **Distribuição:** acervo por categoria 000–900, em gráfico de barras horizontais
- **Filtro por período validado:** `PeriodoForm` (`DateField`) valida as datas
  vindas da URL. Data inválida ou início maior que o fim mostra mensagem de erro
  na tela, sem erro 500, e o filtro não é aplicado
- **Exportação CSV:** usa a mesma base filtrada do dashboard; protege células
  que começam com `=`, `+`, `-` ou `@` (o Excel poderia tratá-las como fórmula)
  e inclui BOM para os acentos abrirem corretamente
- **API JSON:** as mesmas métricas do dashboard, reaproveitando as funções de
  `dashboard.py`
- **Telas sem dados:** `{% empty %}` e mensagem "Sem dados no período."
- **Desempenho:** uma consulta por métrica (4 no total), sem N+1
- **Testes automatizados:** 20 testes (métricas, filtro, dashboard vazio,
  número de consultas, CSV e API)

## Perguntas do dono do sistema (Aula 17, Tarefa 1)
Cada pergunta vira um card, gráfico ou tabela do dashboard:

| Pergunta | Métrica | Onde aparece |
|---|---|---|
| Quantos livros temos e quantos estão disponíveis? | KPIs | Cartões: livros, disponíveis, digitais, físicos |
| Quais autores têm mais livros no acervo? | Ranking | Tabela "Autores com mais livros" |
| Como evoluiu o cadastro de livros mês a mês? | Série no tempo | Gráfico "Livros cadastrados por mês" |
| Como o acervo se distribui entre as categorias 000–900? | Distribuição | Gráfico "Acervo por categoria" |

Observação: o projeto não tem empréstimos, leitores nem organizações
(multi-tenant); por isso as métricas usam o modelo `Livro`.

## Mudanças feitas na P2

| Arquivo | Mudança |
|---|---|
| `acervo/models.py` | Novo campo `criado_em` (data de cadastro) e índice nele, base do filtro por período e da série por mês |
| `acervo/migrations/0002_livro_criado_em.py` | Migration do campo e do índice |
| `acervo/dashboard.py` | **Novo.** Funções de métricas: `kpis`, `ranking_autores`, `livros_por_mes`, `distribuicao_categoria` e `calcular_metricas` |
| `acervo/forms.py` | `PeriodoForm` e `filtrar_periodo` |

## Executar
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Testes: `python manage.py test`

Acesse:
- http://127.0.0.1:8000/livros/
- http://127.0.0.1:8000/livros/novo/
- http://127.0.0.1:8000/dashboard/ (ex.: `?inicio=2026-01-01&fim=2026-03-31`)
- http://127.0.0.1:8000/dashboard/exportar/ (CSV)
- http://127.0.0.1:8000/dashboard/api/ (JSON)
- http://127.0.0.1:8000/admin/

