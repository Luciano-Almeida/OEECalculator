@echo off
setlocal EnableDelayedExpansion

:: Caminho para seu arquivo .env
set ENV_FILE=.env

:: Inicializa variáveis
set POSTGRES_BACKEND_USER=
set POSTGRES_BACKEND_DB=

:: Lê o arquivo .env linha por linha
for /f "tokens=1,2 delims==" %%A in (%ENV_FILE%) do (
    set "var=%%A"
    set "val=%%B"
    if /i "!var!"=="POSTGRES_BACKEND_USER" set POSTGRES_BACKEND_USER=!val!
    if /i "!var!"=="POSTGRES_BACKEND_DB" set POSTGRES_BACKEND_DB=!val!
)

:: Define o nome do arquivo de backup com data/hora
for /f %%i in ('powershell -command "Get-Date -Format yyyyMMdd_HHmmss"') do set TIMESTAMP=%%i
set BACKUP_FILE=backup_!POSTGRES_BACKEND_DB!_!TIMESTAMP!.sql

:: Caminho da Área de Trabalho do usuário atual
set DESKTOP_PATH=%USERPROFILE%\Desktop

:: Faz o dump usando docker exec
echo Fazendo backup do banco de dados...
docker exec -t postgres-db-backend pg_dump -U %POSTGRES_BACKEND_USER% -d %POSTGRES_BACKEND_DB% > "%DESKTOP_PATH%\%BACKUP_FILE%"

if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao exportar o banco de dados.
    pause
    exit /b 1
)

echo Backup salvo com sucesso em: %DESKTOP_PATH%\%BACKUP_FILE%
pause
endlocal
