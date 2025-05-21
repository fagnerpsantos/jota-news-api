# JOTA API

API para o sistema de notícias da JOTA, desenvolvida com Django e Django REST Framework.

## Tecnologias Utilizadas

- Python 3.12
- Django 5.2
- Django REST Framework 3.16
- PostgreSQL 15
- Redis 7
- Celery 5.5
- Docker e Docker Compose
- Nginx

## Requisitos

- Docker e Docker Compose
- Python 3.12 (para desenvolvimento local)
- uv (gerenciador de pacotes Python)

## Configuração do Ambiente

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# Django
DEBUG=0
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=jota_prod
DB_USER=jota_user
DB_PASSWORD=senha-forte-aqui
DB_HOST=db
DB_PORT=5432
DATABASE_URL="postgres://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL="${REDIS_URL}"
CELERY_RESULT_BACKEND="${REDIS_URL}"

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com
EMAIL_NOTIFICATION_ENABLED=True

# Site
SITE_URL=http://localhost
```

## Instalação e Execução

### Com Docker (Recomendado)

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/jota-api.git
   cd jota-api
   ```

2. Crie o arquivo `.env` conforme instruções acima

3. Execute com Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Crie um superusuário:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Acesse a API em http://localhost:80/api/
   - Documentação Swagger: http://localhost:80/api/docs/
   - Documentação ReDoc: http://localhost:80/api/redoc/
   - Admin Django: http://localhost:80/admin/

### Desenvolvimento Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/jota-api.git
   cd jota-api
   ```

2. Instale as dependências:
   ```bash
   pip install uv
   uv pip install -e .
   ```

3. Configure o banco de dados:
   ```bash
   # Opção 1: SQLite (para desenvolvimento rápido)
   # Já configurado por padrão

   # Opção 2: PostgreSQL (recomendado)
   # Configure as variáveis de ambiente DATABASE_URL
   ```

4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

5. Crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```

6. Execute o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

7. Em outro terminal, execute o Celery:
   ```bash
   celery -A jota_api worker -l info
   ```

## Estrutura do Projeto

```
jota-api/
├── conftest.py              # Configurações para testes com pytest
├── docker-compose.yml       # Configuração do Docker Compose
├── Dockerfile               # Configuração do Docker
├── jota_api/                # Aplicação principal
│   ├── asgi.py
│   ├── celery.py            # Configuração do Celery
│   ├── settings.py          # Configurações do Django
│   ├── urls.py              # URLs do projeto
│   └── wsgi.py
├── manage.py                # Script de gerenciamento do Django
├── news/                    # App de notícias
│   ├── admin.py
│   ├── apps.py
│   ├── models.py            # Modelos de dados
│   ├── permissions.py       # Permissões personalizadas
│   ├── serializers.py       # Serializadores da API
│   ├── tasks.py             # Tarefas do Celery
│   ├── tests/               # Testes automatizados
│   └── views.py             # Views da API
├── nginx/                   # Configuração do Nginx
│   └── default.conf
├── pyproject.toml           # Dependências do projeto
├── pytest.ini               # Configuração do pytest
├── static/                  # Arquivos estáticos
├── subscription/            # App de assinaturas
│   ├── admin.py
│   ├── apps.py
│   ├── models.py            # Modelos de planos e assinaturas
│   ├── serializers.py       # Serializadores para planos e assinaturas
│   ├── tests/               # Testes automatizados
│   └── views.py             # Views da API de assinaturas
├── users/                   # App de usuários
└── uv.lock                  # Lock file das dependências
```

## Executando Testes

```bash
# Com Docker
docker-compose exec web pytest

# Localmente
pytest
```

## Endpoints da API

### Autenticação

- `POST /api/token/`: Obter token JWT
- `POST /api/token/refresh/`: Atualizar token JWT

### Notícias

- `GET /api/news/`: Listar notícias
- `POST /api/news/`: Criar notícia (requer autenticação como editor)
- `GET /api/news/{id}/`: Obter detalhes de uma notícia
- `PUT /api/news/{id}/`: Atualizar notícia (requer ser autor ou admin)
- `DELETE /api/news/{id}/`: Excluir notícia (requer ser autor ou admin)
- `POST /api/news/{id}/publish/`: Publicar notícia (requer ser editor)
- `GET /api/news/featured/`: Listar notícias em destaque

### Categorias

- `GET /api/categories/`: Listar categorias
- `POST /api/categories/`: Criar categoria (requer autenticação como admin)

### Usuários

- `GET /api/users/`: Listar usuários (requer autenticação como admin)
- `GET /api/users/me/`: Obter perfil do usuário atual
- `POST /api/users/register/`: Registrar novo usuário

### Assinaturas

- `GET /api/subscription-plans/`: Listar planos de assinatura disponíveis
- `POST /api/subscription-plans/{id}/subscribe/`: Assinar um plano (requer autenticação)
- `GET /api/subscriptions/`: Listar assinaturas (admin vê todas, usuário vê apenas a própria)
- `GET /api/subscriptions/my_subscription/`: Obter detalhes da assinatura do usuário atual
- `POST /api/subscriptions/{id}/renew/`: Renovar uma assinatura (requer ser admin)
- `POST /api/subscriptions/{id}/cancel/`: Cancelar uma assinatura (requer ser admin)

## Planos de Assinatura

O sistema possui dois tipos de planos de assinatura:

- **JOTA Info**: Acesso a conteúdo básico e categorias selecionadas
- **JOTA PRO**: Acesso completo a todo o conteúdo e todas as categorias

## Níveis de Acesso

- **FREE**: Conteúdo gratuito, acessível a todos os usuários
- **PRO**: Conteúdo premium, acessível apenas a usuários com assinatura ativa

## Papéis de Usuário

- **ADMIN**: Acesso total ao sistema
- **EDITOR**: Pode criar e gerenciar notícias
- **READER**: Pode ler notícias de acordo com seu nível de assinatura

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença BSD - veja o arquivo LICENSE para detalhes.