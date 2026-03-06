@echo off
REM Pre-deploy validation script for Windows
REM Executa testes e validações antes do deploy

echo 🚀 Iniciando validação pré-deploy...

REM 1. Verificar se não há arquivos não commitados
echo 📋 Verificando status do git...
git status --porcelain > temp_status.txt
if %errorlevel% neq 0 (
    echo ❌ Erro ao verificar status do git
    exit /b 1
)

for /f %%i in ('type temp_status.txt ^| find /c /v ""') do set status_count=%%i
if %status_count% gtr 0 (
    echo ⚠️  Existem arquivos não commitados
    type temp_status.txt
    set /p continue="Deseja continuar mesmo assim? (y/N): "
    if /i not "!continue!"=="y" (
        echo ❌ Deploy cancelado - Faça commit das mudanças
        del temp_status.txt
        exit /b 1
    )
) else (
    echo ✅ Nenhum arquivo não commitado
)
del temp_status.txt

REM 2. Verificar sintaxe Python
echo 🐍 Verificando sintaxe Python...
python -m py_compile main.py
if %errorlevel% neq 0 (
    echo ❌ Erro de sintaxe em main.py
    exit /b 1
)
echo ✅ Sintaxe Python OK

REM 3. Verificar imports
echo 📦 Verificando imports...
python -c "from main import app; print('✅ Import principal OK')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Erro ao importar main.py
    exit /b 1
)

python -c "from app.routers.main import router; from app.routers.dashboard import router as dashboard_router; print('✅ Imports de routers OK')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Erro nos imports de routers
    exit /b 1
)

echo ✅ Todos os imports OK

REM 4. Executar testes
echo 🧪 Executando testes pré-deploy...
python test_pre_deploy.py
if %errorlevel% neq 0 (
    echo ❌ Testes falharam
    exit /b 1
)
echo ✅ Todos os testes passaram

REM 5. Verificar arquivos críticos
echo 📁 Verificando arquivos críticos...
if not exist "main.py" (
    echo ❌ Arquivo crítico faltando: main.py
    exit /b 1
)
if not exist "app\templates\dashboard.html" (
    echo ❌ Arquivo crítico faltando: dashboard.html
    exit /b 1
)
if not exist "app\routers\dashboard.py" (
    echo ❌ Arquivo crítico faltando: dashboard.py
    exit /b 1
)
if not exist "static\pwa.js" (
    echo ❌ Arquivo crítico faltando: pwa.js
    exit /b 1
)
echo ✅ Todos os arquivos críticos existem

REM 6. Resumo final
echo.
echo 📋 RESUMO DA VALIDAÇÃO:
echo ========================
echo ✅ Todas as validações passaram!
echo.
echo 🚀 PRONTO PARA DEPLOY!
echo.
echo Próximos passos:
echo 1. git push origin main
echo 2. Aguardar deploy no Render
echo 3. Testar em produção

exit /b 0
