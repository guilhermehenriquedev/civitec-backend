# 🐍 Backend Civitec - API Django REST

## 📋 Descrição

O backend do Civitec é uma API REST robusta desenvolvida em Django 5.2.5, responsável por gerenciar toda a lógica de negócio, autenticação e persistência de dados do sistema de gestão municipal.

## 🏗️ Arquitetura

- **Framework**: Django 5.2.5
- **API**: Django REST Framework 3.16.1
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT (JSON Web Tokens)
- **CORS**: Suporte a requisições cross-origin
- **Arquitetura**: Módulos separados por funcionalidade

## 📁 Estrutura do Projeto

```
backend/
├── core/                 # Configurações principais do Django
│   ├── settings.py      # Configurações do projeto
│   ├── urls.py          # URLs principais
│   ├── api_urls.py      # URLs da API
│   └── wsgi.py          # Configuração WSGI
├── users/               # Módulo de usuários e autenticação
├── rh/                  # Recursos Humanos
├── obras/               # Gestão de Obras
├── licitacao/           # Processos Licitatórios
├── tributos/            # Gestão Tributária
├── audit/               # Sistema de Auditoria
├── reporting/           # Relatórios e Analytics
├── manage.py            # Script de gerenciamento Django
├── requirements.txt     # Dependências Python
└── .env                 # Variáveis de ambiente (criar)
```

## 🚀 Como Executar Localmente

### 1. Pré-requisitos

Certifique-se de ter instalado:

- **Python 3.11+**
- **PostgreSQL 13+**
- **pip** (gerenciador de pacotes Python)
- **virtualenv** ou **venv** (ambientes virtuais)

### 2. Clone e Navegação

```bash
# Navegue para o diretório do backend
cd civitec/backend

# Verifique se está no diretório correto
ls -la
# Deve mostrar: manage.py, requirements.txt, core/, etc.
```

### 3. Configuração do Ambiente Virtual

```bash
# Crie um ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
# No Windows:
.venv\Scripts\activate

# No macOS/Linux:
source .venv/bin/activate

# Verifique se está ativo (deve mostrar o caminho do .venv)
which python
```

### 4. Instalação das Dependências

```bash
# Atualize o pip
pip install --upgrade pip

# Instale as dependências
pip install -r requirements.txt

# Verifique se Django foi instalado
python -c "import django; print(django.get_version())"
```

### 5. Configuração do Banco de Dados

#### 5.1 Instalação do PostgreSQL

**macOS (com Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
- Baixe e instale o [PostgreSQL](https://www.postgresql.org/download/windows/)
- Use o instalador oficial

#### 5.2 Criação do Banco de Dados

```bash
# Acesse o PostgreSQL
sudo -u postgres psql

# Crie o banco de dados
CREATE DATABASE civitec;

# Crie um usuário (opcional, mas recomendado)
CREATE USER civitec_user WITH PASSWORD 'sua_senha_segura';

# Conceda privilégios
GRANT ALL PRIVILEGES ON DATABASE civitec TO civitec_user;

# Saia do PostgreSQL
\q
```

### 6. Configuração das Variáveis de Ambiente

Crie um arquivo `.env` na raiz do backend:

```bash
# Arquivo .env
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados
DB_NAME=civitec
DB_USER=civitec_user
DB_PASSWORD=sua_senha_segura
DB_HOST=localhost
DB_PORT=5432

# JWT
ACCESS_TOKEN_LIFETIME_MIN=30
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**⚠️ IMPORTANTE**: Nunca commite o arquivo `.env` no Git!

### 7. Execução das Migrações

```bash
# Certifique-se de que o ambiente virtual está ativo
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate     # Windows

# Execute as migrações
python manage.py makemigrations
python manage.py migrate

# Verifique o status das migrações
python manage.py showmigrations
```

### 8. Criação do Superusuário

```bash
# Crie um usuário administrador
python manage.py createsuperuser

# Siga as instruções para criar:
# - Username
# - Email
# - Password (e confirmação)
```

### 9. Execução do Servidor

```bash
# Inicie o servidor de desenvolvimento
python manage.py runserver

# Ou especifique uma porta específica
python manage.py runserver 8000

# Para permitir acesso externo (cuidado em produção)
python manage.py runserver 0.0.0.0:8000
```

### 10. Verificação da Instalação

Abra seu navegador e acesse:

- **Admin Django**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/
- **Documentação da API**: http://localhost:8000/api/docs/ (se configurado)

## 🔧 Comandos Úteis

### Desenvolvimento

```bash
# Executar testes
python manage.py test

# Verificar problemas
python manage.py check

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell interativo do Django
python manage.py shell

# Backup do banco
python manage.py dumpdata > backup.json

# Restaurar backup
python manage.py loaddata backup.json
```

### Banco de Dados

```bash
# Reset completo do banco (⚠️ CUIDADO!)
python manage.py flush

# Criar migrações para mudanças nos modelos
python manage.py makemigrations [app_name]

# Aplicar migrações
python manage.py migrate [app_name]

# Ver status das migrações
python manage.py showmigrations
```

## 📊 Endpoints da API

### Autenticação
- `POST /api/auth/login/` - Login de usuário
- `POST /api/auth/refresh/` - Renovar token
- `POST /api/auth/logout/` - Logout

### Usuários
- `GET /api/users/` - Listar usuários
- `POST /api/users/` - Criar usuário
- `GET /api/users/{id}/` - Detalhes do usuário
- `PUT /api/users/{id}/` - Atualizar usuário
- `DELETE /api/users/{id}/` - Deletar usuário

### Módulos Específicos
- **RH**: `/api/rh/`
- **Obras**: `/api/obras/`
- **Licitações**: `/api/licitacao/`
- **Tributos**: `/api/tributos/`
- **Auditoria**: `/api/audit/`
- **Relatórios**: `/api/reporting/`

## 🛠️ Desenvolvimento

### Estrutura de um App Django

```
app_name/
├── __init__.py
├── admin.py          # Configuração do admin
├── apps.py           # Configuração do app
├── models.py         # Modelos de dados
├── serializers.py    # Serializers para API
├── views.py          # Views da API
├── urls.py           # URLs do app
└── migrations/       # Migrações do banco
```

### Padrões de Código

- **Models**: Use nomes descritivos e docstrings
- **Views**: Mantenha a lógica simples, use serializers
- **Serializers**: Valide dados de entrada e saída
- **URLs**: Use nomes descritivos e versionamento

## 🔒 Segurança

### Configurações Recomendadas para Produção

```python
# settings.py
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = ['seu-dominio.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies seguros
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 🐛 Solução de Problemas

### Erro: "psycopg2 not found"
```bash
# Instale o psycopg2
pip install psycopg2-binary
```

### Erro: "Database connection failed"
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no arquivo `.env`
- Teste a conexão: `psql -h localhost -U civitec_user -d civitec`

### Erro: "Port already in use"
```bash
# Encontre o processo usando a porta
lsof -i :8000

# Mate o processo
kill -9 <PID>
```

### Erro: "Module not found"
```bash
# Verifique se o ambiente virtual está ativo
which python

# Reinstale as dependências
pip install -r requirements.txt
```

## 📚 Recursos Adicionais

- [Documentação Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [JWT](https://django-rest-framework-simplejwt.readthedocs.io/)

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação
2. Consulte os logs do Django
3. Entre em contato com a equipe de desenvolvimento

---

**Backend Civitec** - API robusta para gestão municipal eficiente.
