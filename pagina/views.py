from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    # Opção 1: Simplesmente retornar um HttpResponse
    # return HttpResponse("<h1>Olá, Django! Esta é a página inicial.</h1>")

    # Opção 2: Renderizar um template HTML (mais comum e recomendado)
    # Vamos criar este template no passo 3.
    context = {
        'titulo': 'Página Inicial do Projeto Django Simples',
        'mensagem': 'Bem-vindo ao nosso projeto que será implantado na AWS!',
    }
    return render(request, 'pagina_inicial/index.html', context)