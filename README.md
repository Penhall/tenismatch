# Análise do Projeto TenisMatch

**Estrutura Geral:**

O projeto TenisMatch é uma aplicação web Django, organizada em torno de três aplicativos principais: `matching`, `profiles` e `users`, além de um diretório `core` para configurações e URLs do projeto. A documentação (`docs`), scripts (`scripts`), arquivos estáticos (`static`) e templates HTML (`templates`) também estão presentes.

**Aplicativos Principais:**

*   `matching`: Este aplicativo parece ser o coração do projeto, responsável pela funcionalidade de correspondência de usuários com base em seus perfis de tênis. Inclui subdiretórios `ml` (machine learning) e `services`, sugerindo o uso de aprendizado de máquina para recomendações. Os arquivos `views.py` e `models.py` indicam que ele gerencia perfis de tênis (`SneakerProfile`) e correspondências (`Match`), utilizando formulários Django e um serviço de recomendação (`TenisMatchRecommender`).
*   `profiles`: Este aplicativo provavelmente gerencia perfis de usuário gerais, além dos perfis de tênis específicos do aplicativo `matching`.
*   `users`: Este aplicativo é responsável pela autenticação e gerenciamento de usuários, incluindo funcionalidades como registro, login e visualização de perfis. Inclui `serializers.py`, indicando que pode haver uma API RESTful ou uso de serialização de dados.

**Tecnologias e Dependências:**

O projeto utiliza Django 5.0 como framework web principal. Outras dependências incluem:

*   `django-environ`: Para gestão de variáveis de ambiente.
*   `pandas`, `numpy`, `scikit-learn`: Bibliotecas de machine learning, reforçando a suspeita de uso de ML no aplicativo `matching`.
*   `python-decouple`: Outra biblioteca para gestão de configurações, similar ao `django-environ`.
*   `pillow`: Para processamento de imagens, o que pode ser relevante para funcionalidades relacionadas a tênis, como upload de fotos.

# Estrutura do Projeto

```
d:/PYTHON/tenismatch/
├── .gitignore
├── asgi.py
├── manage.py
├── README.md
├── requirements.txt
├── apps/
│   ├── matching/                 # App de correspondência de tênis
│   │   ├── ml/                  # Módulos de machine learning
│   │   ├── services/            # Serviços de processamento e recomendação
│   │   └── [outros arquivos]    # Views, models, forms, etc.
│   ├── profiles/                # App de gerenciamento de perfis
│   ├── tenis_admin/             # App administrativa
│   │   ├── static/              # Arquivos estáticos da área admin
│   │   ├── templates/           # Templates específicos para admin
│   │   │   ├── analyst/         # Interface do analista
│   │   │   └── manager/         # Interface do gerente
│   │   └── [outros arquivos]    # Views, models, forms, etc.
│   └── users/                   # App de autenticação e usuários
├── core/                        # Configurações do projeto
├── docs/                        # Documentação
├── media/                       # Arquivos de mídia enviados
├── resources/                   # Recursos estáticos do projeto
├── scripts/                     # Scripts de automação
├── static/                      # Arquivos estáticos
└── templates/                   # Templates HTML
```

# Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd tenismatch
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
DEBUG=True
SECRET_KEY=sua_chave_secreta
DATABASE_URL=sqlite:///db.sqlite3
```

5. Execute as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Crie um superusuário:
```bash
python manage.py createsuperuser
```

7. Inicie o servidor:
```bash
python manage.py runserver
```

# Criação de Perfis Administrativos

## Perfil de Analista

1. Acesse o painel administrativo em `http://localhost:8000/admin`
2. Faça login com as credenciais de superusuário
3. Na seção "Groups", crie um grupo chamado "Analyst" se ainda não existir
4. Na seção "Users", selecione o usuário que será Analista
5. Na seção "Permissions":
   - Marque "Staff status"
   - Em "Groups", adicione o usuário ao grupo "Analyst"
6. O Analista terá acesso ao dashboard em `http://localhost:8000/tenis-admin/analyst/dashboard/`

## Perfil de Gerente

1. Acesse o painel administrativo em `http://localhost:8000/admin`
2. Faça login com as credenciais de superusuário
3. Na seção "Groups", crie um grupo chamado "Manager" se ainda não existir
4. Na seção "Users", selecione o usuário que será Gerente
5. Na seção "Permissions":
   - Marque "Staff status"
   - Em "Groups", adicione o usuário ao grupo "Manager"
6. O Gerente terá acesso ao dashboard em `http://localhost:8000/tenis-admin/manager/dashboard/`

Os Analistas podem:
- Fazer upload de datasets
- Criar e treinar modelos
- Visualizar métricas de treinamento
- Gerar dados sintéticos

Os Gerentes podem:
- Aprovar ou rejeitar modelos
- Visualizar métricas de desempenho
- Monitorar o sistema
- Revisar datasets
