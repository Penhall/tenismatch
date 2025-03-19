@echo off
echo === Configuracao do PostgreSQL para TenisMatch ===
echo.

REM Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Por favor, instale o Python e tente novamente.
    exit /b 1
)

REM Verifica se o PostgreSQL esta instalado
where psql >nul 2>&1
if %errorlevel% neq 0 (
    echo PostgreSQL nao encontrado. Por favor, instale o PostgreSQL e tente novamente.
    echo Voce pode baixar o PostgreSQL em: https://www.postgresql.org/download/windows/
    exit /b 1
)

REM Executa o script Python
echo Executando script de configuracao...
python scripts/setup_postgres.py

if %errorlevel% neq 0 (
    echo Falha ao executar o script de configuracao.
    exit /b 1
)

echo.
echo === Configuracao concluida ===
echo.
echo Para iniciar o servidor, execute:
echo python manage.py runserver
echo.

pause
