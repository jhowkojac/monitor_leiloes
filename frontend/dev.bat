@echo off
echo Iniciando servidor de desenvolvimento React...

REM Configurar PATH temporário
set PATH=%PATH%;C:\Program Files\nodejs

REM Iniciar servidor de desenvolvimento
echo Iniciando Vite...
npm run dev

pause
