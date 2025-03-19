@echo off
REM Script para executar testes de integração com PostgreSQL no Windows
REM Uso: scripts\run_postgres_tests.bat [app_or_test]

echo === Executando testes de integração com PostgreSQL ===
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

REM Obtém o teste ou app a ser executado
set TEST_TO_RUN=apps.tenis_admin.test_transaction
if not "%~1"=="" set TEST_TO_RUN=%~1

REM Executa os testes de integração com configurações específicas
echo Executando testes: %TEST_TO_RUN%
python manage.py test %TEST_TO_RUN% --settings=core.test_settings --keepdb -v 2

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === Testes concluídos com sucesso! ===
) else (
    echo.
    echo === Falha na execução dos testes. Verifique os erros acima. ===
)

exit /b %ERRORLEVEL%
