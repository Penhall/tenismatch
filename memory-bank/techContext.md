# Contexto Técnico

## Tecnologias Principais

- **Django 5.0**: Framework web principal
- **PostgreSQL 15**: Banco de dados relacional
- **Psycopg2**: Driver PostgreSQL para Python
- **Django-environ**: Gerenciamento de variáveis de ambiente
- **Dj-database-url**: Configuração de banco de dados via URL

## Configuração do Banco de Dados

O projeto utiliza PostgreSQL como banco de dados principal. A configuração é feita através de variáveis de ambiente no arquivo `.env`:

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tenismatch
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

## Dependências Relacionadas ao Banco de Dados

- **psycopg2-binary**: Driver PostgreSQL para Python
- **dj-database-url**: Para configuração de banco de dados via URL
- **django-environ**: Para gestão de variáveis de ambiente

## Estrutura de Dados

O banco de dados PostgreSQL contém tabelas para:
- Usuários
- Perfis
- Correspondências
- Modelos de machine learning
- Dados de treinamento
- Métricas de desempenho

## Migrações

As migrações são gerenciadas pelo Django através dos comandos:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Backup e Restauração

O sistema inclui scripts para backup e restauração do banco de dados PostgreSQL:

```bash
# Backup
pg_dump -U seu_usuario -d tenismatch > backup.sql

# Restauração
psql -U seu_usuario -d tenismatch < backup.sql
```

## Testes com PostgreSQL

Os testes são configurados para rodar com PostgreSQL através do pytest. A configuração está no arquivo `pytest.ini`.
