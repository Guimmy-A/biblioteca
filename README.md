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

Acesse:
- http://127.0.0.1:8000/livros/
- http://127.0.0.1:8000/livros/novo/
- http://127.0.0.1:8000/admin/

## Git
O projeto foi organizado para ser enviado ao GitHub. Os 10 commits solicitados devem ser feitos no histórico do Git local, pois não é possível criar commits no GitHub a partir deste arquivo ZIP.
