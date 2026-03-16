@echo off
echo Instalando dependências do frontend React...

REM Configurar PATH temporário
set PATH=%PATH%;C:\Program Files\nodejs

REM Verificar Node.js
echo Verificando Node.js...
node -v
if %errorlevel% neq 0 (
    echo Node.js não encontrado no PATH!
    echo Usando caminho completo...
    set NODE_CMD="C:\Program Files\nodejs\node.exe"
    set NPM_CMD="C:\Program Files\nodejs\npm.cmd"
) else (
    set NODE_CMD=node
    set NPM_CMD=npm
)

REM Verificar npm
echo Verificando npm...
%NPM_CMD% -v

REM Limpar cache
echo Limpando cache do npm...
%NPM_CMD% cache clean --force

REM Instalar dependências
echo Instalando dependências...
%NPM_CMD% install

echo.
echo Instalação concluída!
echo Para iniciar o desenvolvimento:
echo %NPM_CMD% run dev
echo.
pause
