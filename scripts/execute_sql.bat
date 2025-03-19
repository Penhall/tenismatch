@echo off
echo === Executando script SQL para criar o banco de dados e tabelas ===
echo.

REM Definir variáveis
set PGUSER=postgres
set PGPASSWORD=abc123

set PGHOST=localhost
set PGPORT=5432
set SCRIPT_PATH=scripts\create_database.sql

REM Verificar se o PostgreSQL está instalado
where psql >nul 2>&1
if %errorlevel% neq 0 (
    echo PostgreSQL nao encontrado. Por favor, instale o PostgreSQL e tente novamente.
    echo Voce pode baixar o PostgreSQL em: https://www.postgresql.org/download/windows/
    exit /b 1
)

REM Executar o script SQL
echo Executando script SQL...
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -f %SCRIPT_PATH%

if %errorlevel% neq 0 (
    echo Falha ao executar o script SQL.
    exit /b 1
)

echo.
echo === Configuracao concluida ===
echo.
echo Para iniciar o servidor, execute:
echo python manage.py runserver
echo.

pause
