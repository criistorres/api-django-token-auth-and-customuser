# Django API de Autenticação por Email

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.14%2B-red)](https://www.django-rest-framework.org/)

Uma API Django completa com sistema de autenticação customizado que utiliza email em vez de username, implementada com Django REST Framework e autenticação via token, perfeita para quem quer criar apps ultilizando Tokens para autenticação.

## 📋 Características

- ✅ Autenticação baseada em email em vez de username
- ✅ Modelo de usuário customizado
- ✅ Autenticação por token (REST Framework Token Authentication)
- ✅ Class-Based Views para todas as operações
- ✅ Endpoints para signup, login, logout e verificação de token
- ✅ Validação de senhas com confirmação
- ✅ Testes de API com arquivo .rest

## 🛠️ Tecnologias Utilizadas

- [Django](https://www.djangoproject.com/) - Framework web em Python
- [Django REST Framework](https://www.django-rest-framework.org/) - Toolkit para construção de APIs
- [Django REST Framework Token Auth](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication) - Sistema de autenticação por token

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/django-auth-api.git
cd django-auth-api
```

2. Crie e ative um ambiente virtual:
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

6. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## 📊 Estrutura do Projeto

```
project/
├── accounts/              # App para gerenciamento de usuários
│   ├── admin.py           # Configuração do admin
│   ├── models.py          # Modelo de usuário customizado
│   ├── serializers.py     # Serializers para API
│   ├── urls.py            # URLs da API de autenticação
│   └── views.py           # Views para autenticação
├── core/                  # Configuração principal do projeto
│   ├── settings.py        # Configurações do Django
│   └── urls.py            # URLs do projeto
├── manage.py              # Script de gerenciamento do Django
├── requirements.txt       # Dependências do projeto
└── auth_tests.rest        # Arquivo para testar os endpoints da API
```

## 🔌 Endpoints da API

### Signup
- **URL**: `/api/accounts/signup/`
- **Método**: `POST`
- **Corpo da requisição**:
```json
{
  "email": "usuario@exemplo.com",
  "password": "senha_segura123",
  "password_confirm": "senha_segura123",
  "first_name": "Nome",
  "last_name": "Sobrenome"
}
```
- **Resposta de Sucesso**:
```json
{
  "user": {
    "id": 1,
    "email": "usuario@exemplo.com",
    "first_name": "Nome",
    "last_name": "Sobrenome"
  },
  "token": "seu_token_aqui"
}
```

### Login
- **URL**: `/api/accounts/login/`
- **Método**: `POST`
- **Corpo da requisição**:
```json
{
  "email": "usuario@exemplo.com",
  "password": "senha_segura123"
}
```
- **Resposta de Sucesso**:
```json
{
  "token": "seu_token_aqui",
  "user_id": 1,
  "email": "usuario@exemplo.com"
}
```

### Testar Token
- **URL**: `/api/accounts/test-token/`
- **Método**: `GET`
- **Headers**: `Authorization: Token seu_token_aqui`
- **Resposta de Sucesso**:
```json
{
  "message": "Token válido",
  "user": {
    "id": 1,
    "email": "usuario@exemplo.com",
    "first_name": "Nome",
    "last_name": "Sobrenome"
  }
}
```

### Logout
- **URL**: `/api/accounts/logout/`
- **Método**: `POST`
- **Headers**: `Authorization: Token seu_token_aqui`
- **Resposta de Sucesso**:
```json
{
  "message": "Logout realizado com sucesso."
}
```

## 📝 Como Testar

### Usando o arquivo .rest

Se você utiliza o VS Code, instale a extensão [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) e utilize o arquivo `auth_tests.rest` incluído no projeto para testar os endpoints:

```http
### Variáveis
@baseUrl = http://localhost:8000/api
@token = seu_token_aqui

### Registrar um novo usuário
POST {{baseUrl}}/accounts/signup/
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "password": "senha_segura123",
  "password_confirm": "senha_segura123",
  "first_name": "Nome",
  "last_name": "Sobrenome"
}

### Login
POST {{baseUrl}}/accounts/login/
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "password": "senha_segura123"
}

### Testar token (copie o token da resposta do login acima)
GET {{baseUrl}}/accounts/test-token/
Authorization: Token {{token}}

### Logout
POST {{baseUrl}}/accounts/logout/
Authorization: Token {{token}}
```

### Usando curl

```bash
# Signup
curl -X POST http://localhost:8000/api/accounts/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@exemplo.com","password":"senha_segura123","password_confirm":"senha_segura123","first_name":"Nome","last_name":"Sobrenome"}'

# Login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@exemplo.com","password":"senha_segura123"}'

# Testar token
curl -X GET http://localhost:8000/api/accounts/test-token/ \
  -H "Authorization: Token seu_token_aqui"

# Logout
curl -X POST http://localhost:8000/api/accounts/logout/ \
  -H "Authorization: Token seu_token_aqui"
```

## 🔐 Segurança

Para ambientes de produção, lembre-se de:

- Usar HTTPS para todas as comunicações
- Configurar o Django com chaves secretas seguras
- Desativar o modo DEBUG
- Configurar ALLOWED_HOSTS apropriadamente
- Considerar políticas de expiração de token

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## 👤 Autor

- Seu Nome - [GitHub](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- Documentação do Django REST Framework
- Comunidade Django
