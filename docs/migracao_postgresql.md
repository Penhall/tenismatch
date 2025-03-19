# Migração para PostgreSQL

Este documento descreve o processo de migração do banco de dados SQLite para PostgreSQL no projeto TenisMatch.

## Motivação

A migração para PostgreSQL traz diversos benefícios:

1. **Melhor desempenho com grandes volumes de dados**
2. **Suporte a concorrência** - múltiplos usuários podem acessar o banco simultaneamente
3. **Recursos avançados** - índices mais eficientes, tipos de dados JSON nativos, etc.
4. **Maior confiabilidade** - transações ACID completas e recuperação de falhas
5. **Escalabilidade** - melhor suporte para aplicações em crescimento

## Pré-requisitos

- PostgreSQL 14+ instalado
- Python 3.10+
- Dependências do projeto atualizadas (`pip install -r requirements.txt`)

## Configuração do PostgreSQL

### Instalação do PostgreSQL

1. Baixe e instale o PostgreSQL do [site oficial](https://www.postgresql.org/download/)
2. Durante a instalação, defina uma senha para o usuário `postgres`
3. Adicione o PostgreSQL ao PATH do sistema (opcional, mas recomendado)

### Configuração do Banco de Dados

O projeto inclui scripts para facilitar a configuração. Você tem duas opções:

#### Opção 1: Usando o script SQL (Recomendado)

1. Edite o arquivo `scripts/execute_sql.bat` se necessário para ajustar as credenciais:
   ```batch
   set PGUSER=postgres
   set PGPASSWORD=abc123
   set PGHOST=localhost
   set PGPORT=5432
   ```

2. Execute o script:
   ```
   scripts/execute_sql.bat
   ```

3. Renomeie as tabelas para os nomes que o Django espera:
   ```
   scripts/execute_rename_tables.bat
   ```

4. Aplique as migrações:
   ```
   python manage.py migrate --fake-initial
   ```

Este processo irá:
- Criar o banco de dados `tenismatch`
- Criar todas as tabelas necessárias
- Renomear as tabelas para os nomes que o Django espera
- Marcar as migrações como aplicadas
- Criar um superusuário com as credenciais:
  - Username: Admin
  - Password: abc123
  - Email: admin@grupo4.com

#### Opção 2: Usando o Django

1. Edite o arquivo `.env` na raiz do projeto com suas credenciais:
   ```
   DB_NAME=tenismatch
   DB_USER=postgres
   DB_PASSWORD=abc123
   DB_HOST=localhost
   DB_PORT=5432
   ```

2. Execute o comando para aplicar as migrações:
   ```
   python manage.py migrate
   ```

3. Crie um superusuário:
   ```
   python manage.py createsuperuser
   ```

## Alterações Realizadas

### 1. Dependências Adicionadas
- `psycopg2-binary`: Adaptador PostgreSQL para Python
- `dj-database-url`: Facilita configuração de URLs de banco de dados

### 2. Configurações Atualizadas
- `core/settings.py`: Configuração do PostgreSQL como banco de dados
- `.env`: Configurações de ambiente para o PostgreSQL

### 3. Limpeza de Dados
- Pasta `media/models/` esvaziada
- Pasta `media/datasets/` esvaziada
- Arquivo `db.sqlite3` removido

### 4. Scripts Criados
- `scripts/create_database.sql`: Script SQL para criar o banco de dados e tabelas
- `scripts/execute_sql.bat`: Script para executar o script SQL
- `scripts/rename_tables.sql`: Script SQL para renomear as tabelas para os nomes que o Django espera
- `scripts/execute_rename_tables.bat`: Script para executar o script de renomeação de tabelas
- `scripts/test_postgres_connection.py`: Script Python para testar a conexão com o PostgreSQL

## Troubleshooting

### Erro de Conexão com o PostgreSQL

Se você encontrar erros como "could not connect to server" ou "connection refused":

1. Verifique se o serviço do PostgreSQL está em execução
   - Windows: Verifique o "Serviços" no Painel de Controle
   - Linux: `sudo systemctl status postgresql`

2. Verifique as credenciais nos scripts ou no arquivo `.env`

3. Teste a conexão diretamente:
   ```
   python scripts/test_postgres_connection.py
   ```

### Erro de Codificação

Se você encontrar erros de codificação como "UnicodeDecodeError":

1. Verifique se o PostgreSQL está configurado para usar UTF-8
2. Use o script SQL (`scripts/execute_sql.bat`) em vez das migrações do Django

### Erro nas Migrações

Se houver erros durante a aplicação das migrações:

1. Verifique os logs de erro
2. Tente usar o comando `--fake` ou `--fake-initial`:
   ```
   python manage.py migrate --fake-initial
   ```
3. Se as tabelas já existem mas com nomes diferentes, use o script de renomeação:
   ```
   scripts/execute_rename_tables.bat
   ```

## Próximos Passos

1. Testar todas as funcionalidades do sistema com o novo banco de dados
2. Otimizar consultas para PostgreSQL
3. Implementar backups automáticos
4. Configurar monitoramento de performance

## Referências

- [Documentação do PostgreSQL](https://www.postgresql.org/docs/)
- [Django com PostgreSQL](https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes)
