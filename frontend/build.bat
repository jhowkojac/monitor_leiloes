@echo off
echo Build do frontend React para produção...

REM Configurar PATH temporário
set PATH=%PATH%;C:\Program Files\nodejs

REM Verificar se node_modules existe
if not exist node_modules (
    echo Instalando dependências primeiro...
    npm install
)

REM Build para produção
echo Iniciando build de produção...
npm run build

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build concluído com sucesso!
    echo 📁 Arquivos gerados em: dist/
    echo 🌐 Pronto para deploy no Render/Vercel/Netlify
    echo.
    echo Para testar localmente:
    echo npm run preview
) else (
    echo.
    echo ❌ Erro no build!
    echo Verifique os erros acima e tente novamente.
)

echo.
pause
