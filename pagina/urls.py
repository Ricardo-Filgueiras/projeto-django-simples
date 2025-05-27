from django.urls import path
from . import views  # Importa as views do app atual (pagina_inicial)

app_name = 'pagina' # Namespace para as URLs deste app (opcional, mas boa prática)

urlpatterns = [
    path('', views.index, name='index'), # Mapeia a URL raiz do app para a view 'index'
]