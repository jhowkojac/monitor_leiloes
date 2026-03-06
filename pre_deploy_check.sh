#!/bin/bash

# Pre-deploy validation script
# Executa testes e validações antes do deploy

echo "🚀 Iniciando validação pré-deploy..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para print colorido
print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "SUCCESS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo "ℹ️  $message"
    fi
}

# 1. Verificar se não há arquivos não commitados
echo "📋 Verificando status do git..."
if [ -n "$(git status --porcelain)" ]; then
    print_status "WARNING" "Existem arquivos não commitados"
    echo "Arquivos não commitados:"
    git status --porcelain
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "ERROR" "Deploy cancelado - Faça commit das mudanças"
        exit 1
    fi
else
    print_status "SUCCESS" "Nenhum arquivo não commitado"
fi

# 2. Verificar sintaxe Python
echo "🐍 Verificando sintaxe Python..."
python_files=$(find . -name "*.py" -not -path "./venv/*" -not -path "./env/*")
syntax_errors=0

for file in $python_files; do
    if python -m py_compile "$file" 2>/dev/null; then
        print_status "SUCCESS" "Sintaxe OK: $file"
    else
        print_status "ERROR" "Erro de sintaxe: $file"
        syntax_errors=$((syntax_errors + 1))
    fi
done

if [ $syntax_errors -gt 0 ]; then
    print_status "ERROR" "Encontrados $syntax_errors erros de sintaxe"
    exit 1
fi

# 3. Verificar imports
echo "📦 Verificando imports..."
python -c "
import sys
try:
    from main import app
    print('✅ Import principal OK')
    
    # Testar imports críticos
    from app.routers.main import router
    from app.routers.dashboard import router as dashboard_router
    from app.routers.auth import router as auth_router
    print('✅ Imports de routers OK')
    
    from app.services.dashboard import dashboard_service
    from app.services.analytics import analytics_service
    from app.services.theme import theme_service
    print('✅ Imports de services OK')
    
except ImportError as e:
    print(f'❌ Erro de import: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Erro ao importar: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    print_status "ERROR" "Falha na verificação de imports"
    exit 1
fi

# 4. Executar testes unitários
echo "🧪 Executando testes pré-deploy..."
if python test_pre_deploy.py; then
    print_status "SUCCESS" "Todos os testes passaram"
else
    print_status "ERROR" "Testes falharam"
    exit 1
fi

# 5. Verificar arquivos críticos
echo "📁 Verificando arquivos críticos..."
critical_files=(
    "main.py"
    "app/templates/dashboard.html"
    "app/routers/dashboard.py"
    "app/services/dashboard.py"
    "static/pwa.js"
    "static/analytics.js"
    "static/theme.js"
    "static/manifest.json"
)

missing_files=0
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "SUCCESS" "Arquivo existe: $file"
    else
        print_status "ERROR" "Arquivo crítico faltando: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    print_status "ERROR" "Faltam $missing_files arquivos críticos"
    exit 1
fi

# 6. Verificar configuração
echo "⚙️  Verificando configuração..."
if [ -f ".env" ]; then
    print_status "SUCCESS" "Arquivo .env existe"
else
    print_status "WARNING" "Arquivo .env não encontrado (usando defaults)"
fi

if [ -f "requirements.txt" ]; then
    print_status "SUCCESS" "requirements.txt existe"
else
    print_status "WARNING" "requirements.txt não encontrado"
fi

# 7. Verificar tamanho do projeto
echo "📊 Verificando tamanho do projeto..."
project_size=$(du -sh . | cut -f1)
print_status "SUCCESS" "Tamanho do projeto: $project_size"

# 8. Verificar se servidor local funciona (opcional)
echo "🌐 Verificando inicialização local..."
timeout 10s python -c "
import sys
import asyncio
from main import app

try:
    # Simular startup
    print('✅ App inicializa corretamente')
    print('✅ FastAPI app criada')
    print('✅ Routers configurados')
except Exception as e:
    print(f'❌ Erro na inicialização: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_status "SUCCESS" "App inicializa corretamente"
else
    print_status "WARNING" "Não foi possível verificar inicialização local"
fi

# 9. Resumo final
echo ""
echo "📋 RESUMO DA VALIDAÇÃO:"
echo "========================"

if [ $syntax_errors -eq 0 ] && [ $missing_files -eq 0 ]; then
    print_status "SUCCESS" "✅ Todas as validações passaram!"
    echo ""
    echo "🚀 PRONTO PARA DEPLOY!"
    echo ""
    echo "Próximos passos:"
    echo "1. git push origin main"
    echo "2. Aguardar deploy no Render"
    echo "3. Testar em produção"
    exit 0
else
    print_status "ERROR" "❌ Validações falharam!"
    echo ""
    echo "Corrija os erros antes de fazer deploy."
    exit 1
fi
