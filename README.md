# Biblioteca — Consolidado Aulas 04 e 05

Projeto Django de acervo bibliográfico baseado nas atividades das Aulas 04 e 05.

## Funcionalidades
- Cadastro de livros
- Tipo de acervo: Digital ou Físico
- Categoria por classificação 000 a 900
- Pesquisa por nome/título, tipo de acervo e categoria
- Django Admin
- Views, URLs, templates e ModelForm
- Layout com herança de templates
- SQLite para facilitar a execução local
- Dashboard (Aula 17): KPIs, ranking de autores, livros por mês, acervo por categoria
- Filtro por período validado (`PeriodoForm`), gráficos com `json_script` + Chart.js
- Exportação CSV e API JSON usando a mesma base filtrada

## Perguntas do dono do sistema (Aula 17, Tarefa 1)
Cada pergunta vira um card, gráfico ou tabela do dashboard:

| Pergunta | Métrica | Onde aparece |
|---|---|---|
| Quantos livros temos e quantos estão disponíveis? | KPIs (`aggregate` + `Count` com filtro) | Cartões: livros, disponíveis, digitais, físicos |
| Quais autores têm mais livros no acervo? | Ranking (`values` + `annotate` + `order_by`) | Tabela "Autores com mais livros" |
| Como evoluiu o cadastro de livros mês a mês? | Série no tempo (`TruncMonth`) | Gráfico de barras (Chart.js) |
| Como o acervo se distribui entre as categorias 000–900? | Distribuição (`values` + `annotate`) | Gráfico de barras horizontais (Chart.js) |

Observação: o projeto não tem empréstimos, leitores nem organizações (multi-tenant); por isso as métricas usam o modelo `Livro`.

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

## Git
O projeto foi organizado para ser enviado ao GitHub. Os 10 commits solicitados devem ser feitos no histórico do Git local, pois não é possível criar commits no GitHub a partir deste arquivo ZIP.
