# Testes com PostgreSQL no Django

Este documento explica como adaptar e executar testes no Django usando PostgreSQL como banco de dados de teste.

## Introdução

Por padrão, o Django usa SQLite como banco de dados para testes, mesmo quando o banco de dados principal é PostgreSQL. Isso pode levar a problemas, pois o SQLite e o PostgreSQL têm comportamentos diferentes em relação a transações, constraints, tipos de dados e outras funcionalidades.

Para garantir que os testes reflitam com precisão o comportamento do aplicativo em produção, é recomendável usar PostgreSQL também para os testes.

## Adaptações Realizadas

### Testes de Integração

O arquivo `apps/tenis_admin/tests_integration.py` foi adaptado para usar PostgreSQL nos testes de integração. As principais mudanças foram:

1. **Uso de TransactionTestCase**: Em vez de `TestCase`, usamos `TransactionTestCase` para lidar melhor com transações no PostgreSQL.

2. **Configuração de Bancos de Dados**: Adicionamos `databases = '__all__'` para garantir que todos os bancos de dados configurados sejam usados nos testes.

3. **Verificação de Conexão**: Adicionamos código para verificar a conexão com o PostgreSQL no início dos testes.

4. **Arquivos Temporários**: Usamos o módulo `tempfile` para criar arquivos temporários para os testes, garantindo que sejam limpos após o uso.

5. **Limpeza de Recursos**: Adicionamos um método `tearDown` para garantir que todos os recursos sejam limpos após cada teste.

### Testes Adicionais

Foram criados testes adicionais para demonstrar diferentes abordagens de teste com PostgreSQL:

1. **Teste Simples** (`apps/tenis_admin/test_simple.py`): Um teste simples que verifica a conexão com o PostgreSQL sem depender de modelos do Django ou de migrações.

2. **Teste de Transação** (`apps/tenis_admin/test_transaction.py`): Um teste que usa `TransactionTestCase` e cria uma tabela temporária para demonstrar operações de banco de dados com PostgreSQL.

3. **Teste com Pytest** (`apps/tenis_admin/test_integration_pytest.py`): Um exemplo de teste usando pytest com PostgreSQL.

## Configurações Específicas para Testes

Foi criado um arquivo de configurações específicas para testes em `core/test_settings.py`. Este arquivo estende as configurações padrão do projeto e adiciona configurações otimizadas para testes com PostgreSQL:

1. **Banco de Dados de Teste Dedicado**: Configuramos um banco de dados específico para testes chamado `test_tenismatch`.

2. **Otimizações de Performance**:
   - Desativamos a serialização de dados para testes mais rápidos
   - Usamos um hasher de senha mais rápido (MD5) para testes
   - Desativamos o cache
   - Reduzimos o nível de logging para WARNING

3. **Configurações de Mídia**: Usamos um diretório temporário para arquivos de mídia em testes.

4. **Configurações de Email**: Usamos o backend de email em memória para testes.

5. **Desativação de CSRF**: Desativamos a proteção CSRF para facilitar os testes.

Para usar estas configurações, execute os testes com o parâmetro `--settings=core.test_settings`:

```bash
python manage.py test apps.tenis_admin.test_transaction --settings=core.test_settings
```

## Como Executar os Testes

### Usando o Django Test Runner

#### Script Python

```bash
python scripts/run_postgres_tests.py [app_or_test]
```

Este script:
- Verifica se o PostgreSQL está em execução
- Executa os testes especificados (ou `apps.tenis_admin.test_transaction` por padrão)
- Exibe os resultados

Exemplos:
```bash
python scripts/run_postgres_tests.py                           # Executa o teste de transação padrão
python scripts/run_postgres_tests.py apps.tenis_admin.test_simple  # Executa o teste simples
python scripts/run_postgres_tests.py apps.tenis_admin          # Executa todos os testes do app tenis_admin
```

#### Script Batch (Windows)

```bash
scripts\run_postgres_tests.bat [app_or_test]
```

Este script:
- Verifica se o PostgreSQL está em execução
- Executa os testes especificados (ou `apps.tenis_admin.test_transaction` por padrão)
- Exibe os resultados

Exemplos:
```bash
scripts\run_postgres_tests.bat                           # Executa o teste de transação padrão
scripts\run_postgres_tests.bat apps.tenis_admin.test_simple  # Executa o teste simples
scripts\run_postgres_tests.bat apps.tenis_admin          # Executa todos os testes do app tenis_admin
```

#### Comando Django Diretamente

```bash
python manage.py test apps.tenis_admin.test_transaction --settings=core.test_settings --keepdb -v 2
```

O parâmetro `--keepdb` mantém o banco de dados de teste entre execuções, o que acelera os testes subsequentes.

### Usando Pytest

Também foi adicionado suporte para executar testes com pytest, que oferece recursos adicionais como execução paralela, fixtures mais poderosas e relatórios mais detalhados.

#### Script Python

```bash
python scripts/run_pytest.py [args]
```

Este script:
- Verifica se o pytest está instalado e o instala se necessário
- Verifica a conexão com o PostgreSQL
- Cria o banco de dados de teste se não existir
- Executa os testes com pytest
- Exibe os resultados

Você pode passar argumentos adicionais para o pytest:

```bash
python scripts/run_pytest.py -v -m integration
```

#### Script Batch (Windows)

```bash
scripts\run_pytest.bat [args]
```

Este script:
- Verifica se o PostgreSQL está em execução
- Verifica se o banco de dados de teste existe e o cria se necessário
- Instala o pytest se necessário
- Executa os testes com pytest
- Exibe os resultados

Você pode passar argumentos adicionais para o pytest:

```bash
scripts\run_pytest.bat -v -m integration
```

#### Comando Pytest Diretamente

```bash
pytest apps/tenis_admin/test_integration_pytest.py -v --reuse-db
```

## Criando Novos Testes com PostgreSQL

### Usando o Django Test Framework

#### Teste Simples

```python
from django.test import TestCase
import psycopg2

class SimpleTestCase(TestCase):
    """Teste simples para verificar a conexão com o PostgreSQL."""
    
    def test_postgresql_connection(self):
        """Testa a conexão com o PostgreSQL."""
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(
            dbname='tenismatch',
            user='postgres',
            password='abc123',
            host='localhost',
            port='5432'
        )
        
        # Criar um cursor
        cursor = conn.cursor()
        
        # Executar uma consulta simples
        cursor.execute("SELECT version();")
        
        # Obter o resultado
        version = cursor.fetchone()
        
        # Fechar cursor e conexão
        cursor.close()
        conn.close()
        
        # Verificar se a versão foi obtida
        self.assertIsNotNone(version)
        self.assertIn('PostgreSQL', version[0])
```

#### Teste com TransactionTestCase

```python
from django.test import TransactionTestCase

class MeuTeste(TransactionTestCase):
    databases = '__all__'
    
    def setUp(self):
        # Configuração do teste
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        self.temp_file.write(b'dados,de,teste')
        self.temp_file.close()
    
    def tearDown(self):
        # Limpeza após o teste
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_exemplo(self):
        # Seu código de teste aqui
        pass
```

### Usando Pytest

```python
import pytest

# Marca o teste como teste de integração e que requer PostgreSQL
@pytest.mark.integration
@pytest.mark.postgres
@pytest.mark.django_db(transaction=True)
def test_exemplo(analyst_client, temp_csv_file):
    # Seu código de teste aqui
    # Usa as fixtures definidas em conftest.py
    pass
```

O arquivo `conftest.py` na raiz do projeto define várias fixtures úteis para testes:

- `analyst_user`: Cria um usuário analista
- `manager_user`: Cria um usuário gerente
- `analyst_client`: Cria um cliente autenticado como analista
- `manager_client`: Cria um cliente autenticado como gerente
- `temp_csv_file`: Cria um arquivo CSV temporário

## Considerações sobre PostgreSQL vs SQLite

### Diferenças Importantes

1. **Transações**: PostgreSQL suporta transações aninhadas usando savepoints, enquanto SQLite tem suporte limitado.

2. **Constraints**: PostgreSQL aplica constraints de forma mais rigorosa que SQLite.

3. **Tipos de Dados**: PostgreSQL tem suporte a mais tipos de dados, como arrays, JSON, etc.

4. **Case Sensitivity**: PostgreSQL é case-sensitive em consultas por padrão, enquanto SQLite não é.

5. **Concorrência**: PostgreSQL lida melhor com acessos concorrentes.

### Quando Usar PostgreSQL para Testes

- Testes de integração que envolvem múltiplas transações
- Testes que dependem de funcionalidades específicas do PostgreSQL
- Testes que precisam refletir com precisão o comportamento em produção
- Testes que envolvem concorrência ou acesso simultâneo

## Otimizando a Execução de Testes

### Reutilização do Banco de Dados

O parâmetro `--keepdb` (Django) ou `--reuse-db` (pytest) mantém o banco de dados de teste entre execuções, o que acelera os testes subsequentes:

```bash
python manage.py test --keepdb --settings=core.test_settings
pytest --reuse-db
```

### Testes Paralelos

Para executar testes em paralelo, você pode usar o pytest com o plugin pytest-xdist:

```bash
pip install pytest-xdist
pytest apps/tenis_admin/test_integration_pytest.py -v --reuse-db -n 4
```

O arquivo `pytest.ini` na raiz do projeto já está configurado para usar as configurações de teste e outras otimizações:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.test_settings
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db --no-migrations
testpaths = apps
markers =
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    postgres: marks tests that require PostgreSQL
```

## Troubleshooting

### Erro de Conexão

Se você encontrar erros como "could not connect to server" ou "connection refused":

1. Verifique se o serviço do PostgreSQL está em execução
   - Windows: Verifique o "Serviços" no Painel de Controle
   - Linux: `sudo systemctl status postgresql`

2. Verifique as credenciais nos scripts ou no arquivo `.env`

3. Teste a conexão diretamente:
   ```
   python scripts/test_postgres_connection.py
   ```

### Erro nas Migrações

Se houver erros durante a aplicação das migrações:

1. Verifique os logs de erro
2. Tente usar o comando `--fake` ou `--fake-initial`:
   ```
   python manage.py migrate --fake-initial
   ```

### Testes Lentos

Se os testes estiverem muito lentos:

1. Use `--keepdb` (Django) ou `--reuse-db` (pytest) para reutilizar o banco de dados de teste:
   ```
   python manage.py test --keepdb
   pytest --reuse-db
   ```

2. Use pytest com execução paralela:
   ```
   pytest -n 4
   ```

3. Verifique se as configurações de teste estão otimizadas (veja `core/test_settings.py`).

## Referências

- [Django Testing with PostgreSQL](https://docs.djangoproject.com/en/5.0/topics/testing/overview/#the-test-database)
- [TransactionTestCase vs TestCase](https://docs.djangoproject.com/en/5.0/topics/testing/tools/#django.test.TransactionTestCase)
- [Django Database Settings for Tests](https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-DATABASE-TEST)
- [Django Test Performance](https://docs.djangoproject.com/en/5.0/topics/testing/advanced/#improving-performance)
- [Pytest Django](https://pytest-django.readthedocs.io/en/latest/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
