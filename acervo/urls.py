from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_livros, name="inicio"),
    path("livros/", views.lista_livros, name="lista"),
    path("livros/novo/", views.novo_livro, name="novo"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/exportar/", views.exportar_csv, name="exportar_csv"),
    path("dashboard/api/", views.dashboard_api, name="dashboard_api"),
]
