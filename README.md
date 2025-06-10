# Guia de Deploy: Aplicação Django em um Servidor EC2 (Amazon Linux 2023)

Este documento detalha o processo passo a passo para implantar uma aplicação Django em uma instância EC2 da AWS, utilizando Nginx e Gunicorn.

## Etapa 1: Criar e Configurar a Instância EC2

O primeiro passo é criar o servidor virtual na AWS.

1.  **Acessar o Console EC2:** Faça login na AWS, procure e acesse o serviço **EC2**.
2.  **Iniciar Instância:**
    * Clique em **"Launch instances"**.
    * **Nome:** Dê um nome para o servidor (ex: `servidor-django`).
    * **AMI (Amazon Machine Image):** Selecione **Amazon Linux 2023**.
    * **Tipo de Instância:** Escolha uma do nível gratuito, como `t2.micro`.
3.  **Criar Par de Chaves (Key Pair):**
    * Clique em **"Create new key pair"** para acesso SSH.
    * Dê um nome à chave (ex: `chave-django-app`).
    * Mantenha o formato `.pem`.
    * Clique em **"Create key pair"** e salve o arquivo `.pem` baixado em um local seguro.
4.  **Configurar Regras de Rede (Security Group):**
    * Selecione **"Create security group"**.
    * Adicione as seguintes regras de entrada (Inbound rules):
        * **Tipo:** `SSH` | **Origem:** `Anywhere` (ou `My IP` para mais segurança)
        * **Tipo:** `HTTP` | **Origem:** `Anywhere` (0.0.0.0/0)
        * **Tipo:** `HTTPS` | **Origem:** `Anywhere` (0.0.0.0/0)
5.  **Iniciar a Instância:** Revise as configurações e clique em **"Launch instance"**.

## Etapa 2: Conectar-se à Instância EC2

Após a instância estar com o status "Running", conecte-se a ela via SSH.

1.  **Obter o IP Público:** No painel do EC2, selecione a instância e copie o **"Public IPv4 address"**.
2.  **Conectar via Terminal:** Abra seu terminal local (PowerShell, cmd, Terminal do macOS/Linux) e use o comando `ssh`.
    ```bash
    # Substitua os placeholders pelos seus valores
    ssh -i /caminho/para/sua/chave-django-app.pem ec2-user@SEU_IP_PUBLICO
    ```
    > **Nota:** Para o Amazon Linux, o nome de usuário padrão é `ec2-user`. Para o Ubuntu, seria `ubuntu`.

## Etapa 3: Instalar e Configurar o Ambiente no Servidor

Com o acesso ao servidor, vamos instalar o software base.

1.  **Atualizar o Servidor:**
    ```bash
    sudo dnf update -y
    ```
2.  **Instalar Softwares Essenciais:**
    ```bash
    sudo dnf install python3-pip python3-devel nginx git -y
    ```
3.  **Iniciar e Habilitar o Nginx:**
    ```bash
    sudo systemctl start nginx
    sudo systemctl enable nginx
    ```
    > **Verificação:** Acesse `http://SEU_IP_PUBLICO` no navegador. Você deve ver a página "Welcome to nginx!".

## Etapa 4: Implantar o Código da Aplicação Django

Agora, vamos trazer o código do projeto para o servidor.

1.  **Clonar o Repositório Git:**
    ```bash
    # Substitua pela URL do seu repositório
    git clone [https://github.com/seu-usuario/projeto-django-simples.git](https://github.com/seu-usuario/projeto-django-simples.git)
    ```
2.  **Acessar o Diretório do Projeto:**
    ```bash
    # Substitua pelo nome do seu repositório
    cd projeto-django-simples
    ```
3.  **Criar e Ativar o Ambiente Virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Seu prompt do terminal deve agora começar com `(venv)`.

4.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    > **Importante:** Certifique-se de que seu `requirements.txt` contém `django` e `gunicorn`. Se o Gunicorn não estiver lá, instale-o manualmente com `pip install gunicorn`.

## Etapa 5: Configurar e Testar a Aplicação Django

Vamos configurar a aplicação para o ambiente de produção.

1.  **Criar o Arquivo `.env`:**
    ```bash
    nano .env
    ```
    Cole o seguinte conteúdo, ajustando os valores:
    ```env
    DJANGO_SECRET_KEY='sua-chave-secreta-gerada-aqui'
    DJANGO_DEBUG=False
    DJANGO_ALLOWED_HOSTS=SEU_IP_PUBLICO_AQUI
    ```
    * Para gerar uma chave secreta: `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
    * Salve e saia do nano (`Ctrl+X`, `Y`, `Enter`).

2.  **Executar Comandos de Manutenção do Django:**
    ```bash
    # Coletar arquivos estáticos
    python manage.py collectstatic

    # Aplicar migrações do banco de dados
    python manage.py migrate
    ```

## Etapa 6: Configurar o Gunicorn como Serviço

Para garantir que a aplicação rode de forma contínua, criamos um serviço `systemd`.

1.  **Criar o Arquivo de Serviço do Gunicorn:**
    > **Nota:** Este comando usa um caminho absoluto. Você pode executá-lo de qualquer diretório.
    ```bash
    sudo nano /etc/systemd/system/gunicorn.service
    ```
2.  **Adicionar a Configuração do Serviço:**
    ```ini
    [Unit]
    Description=gunicorn daemon for projeto-django-simples
    After=network.target

    [Service]
    User=ec2-user
    Group=nginx
    WorkingDirectory=/home/ec2-user/projeto-django-simples
    ExecStart=/home/ec2-user/projeto-django-simples/venv/bin/gunicorn --workers 3 --bind unix:/home/ec2-user/projeto-django-simples/gunicorn.sock meuapp.wsgi:application

    [Install]
    WantedBy=multi-user.target
    ```
    > **Atenção:** Verifique se os caminhos (`WorkingDirectory`, `ExecStart`) e o nome do arquivo wsgi (`meuapp.wsgi:application`) correspondem à sua estrutura de projeto.

3.  **Iniciar e Habilitar o Serviço Gunicorn:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn
    ```
4.  **Verificar o Status:**
    ```bash
    sudo systemctl status gunicorn
    ```
    Procure pela mensagem `Active: active (running)`.

## Etapa 7: Configurar o Nginx como Proxy Reverso

Esta é a etapa final, onde conectamos a internet ao Gunicorn através do Nginx.

1.  **Criar o Arquivo de Configuração do Nginx:**
    ```bash
    sudo nano /etc/nginx/conf.d/django-app.conf
    ```
2.  **Adicionar a Configuração do Nginx:**
    ```nginx
    server {
        listen 80;
        server_name SEU_IP_PUBLICO_AQUI;

        location = /favicon.ico { access_log off; log_not_found off; }

        location /static/ {
            alias /home/ec2-user/projeto-django-simples/staticfiles/;
        }

        location / {
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass http://unix:/home/ec2-user/projeto-django-simples/gunicorn.sock;
        }
    }
    ```
    * Substitua `SEU_IP_PUBLICO_AQUI` pelo seu IP e verifique se os caminhos `alias` e `proxy_pass` estão corretos.

3.  **Ajustar Permissões do Diretório Home:**
    ```bash
    chmod 755 /home/ec2-user
    ```
4.  **Testar e Reiniciar o Nginx:**
    ```bash
    # Testar a sintaxe da configuração
    sudo nginx -t

    # Reiniciar o Nginx para aplicar as mudanças
    sudo systemctl restart nginx
    ```

### **Conclusão**

Acesse `http://SEU_IP_PUBLICO` no seu navegador. Se tudo correu bem, sua aplicação Django estará online. Parabéns!
