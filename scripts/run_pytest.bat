@echo off
REM Script para executar testes com pytest no Windows
REM Uso: scripts\run_pytest.bat [args]
REM Exemplos:
REM     scripts\run_pytest.bat                           # Executa todos os testes
REM     scripts\run_pytest.bat apps/tenis_admin          # Executa testes do módulo tenis_admin
REM     scripts\run_pytest.bat -v -m integration         # Executa testes de integração com verbose
REM     scripts\run_pytest.bat -v -m "not integration"   # Executa testes que não são de integração

echo === Executando testes com pytest ===
echo.

REM Verifica se o PostgreSQL está em execução
echo Verificando se o PostgreSQL está em execução...
pg_isready -h localhost -p 5432 -U postgres
if %ERRORLEVEL% NEQ 0 (
    echo Erro: PostgreSQL não está em execução ou não está acessível.
    echo Verifique se o serviço do PostgreSQL está iniciado.
    exit /b 1
)

echo PostgreSQL está em execução.
echo.

REM Verifica se o banco de dados de teste existe
echo Verificando se o banco de dados de teste existe...
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT 1 FROM pg_database WHERE datname='test_tenismatch'" | findstr /C:"1 row" > nul
if %ERRORLEVEL% NEQ 0 (
    echo Banco de dados de teste não encontrado. Criando...
    psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE test_tenismatch;"
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao criar o banco de dados de teste.
        exit /b 1
    )
    echo Banco de dados de teste criado com sucesso.
) else (
    echo Banco de dados de teste já existe.
)
echo.

REM Verifica se o pytest está instalado
python -c "import pytest" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Pytest não está instalado. Instalando...
    pip install pytest pytest-django pytest-xdist
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao instalar o pytest.
        exit /b 1
    )
)

REM Executa os testes com pytest
echo Executando testes com pytest...

REM Se não houver argumentos, executa os testes de integração
if "%~1"=="" (
    pytest apps/tenis_admin/test_integration_pytest.py -v --reuse-db
) else (
    REM Se houver argumentos, passa-os para o pytest
    pytest %* --reuse-db
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === Testes concluídos com sucesso! ===
) else (
    echo.
    echo === Falha na execução dos testes. Verifique os erros acima. ===
)

exit /b %ERRORLEVEL%
