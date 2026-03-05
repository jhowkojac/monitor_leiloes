"""Monitor de Leilões - FastAPI Application"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import router
from app.servico import servico_leiloes
from app.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    InputValidationMiddleware,
    APITokenMiddleware
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup
    print("Monitor de Leiloes iniciando...")
    print("Servicos de leiloes configurados")
    print("Seguranca configurada")
    
    # Inicializa o cache com dados (em background para não bloquear)
    import asyncio
    try:
        print("Inicializando cache com dados dos leiloes...")
        # Inicia em background para não bloquear startup
        task = asyncio.create_task(servico_leiloes.atualizar())
        print("Cache sendo inicializado em background...")
        
        # Espera um pouco para ter dados iniciais
        await asyncio.sleep(3)
        
        # Força uma atualização para garantir dados
        try:
            await servico_leiloes.atualizar()
            print("Cache inicializado com sucesso!")
        except Exception as e:
            print(f"Erro na atualizacao inicial: {e}")
            
    except Exception as e:
        print(f"Erro ao inicializar cache: {e}")
        print("Use /init para forcar atualizacao manual")
    
    yield
    # Shutdown
    print("Monitor de Leiloes encerrando...")


app = FastAPI(
    title="Monitor de Leilões - VERSÃO CORRIGIDA",
    description="API para monitoramento de leilões de veículos",
    version="1.0.2",  # Forçar deploy com import os corrigido
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configura middlewares de segurança (em ordem inversa de execução)
# Em produção, todos os middlewares ativos
# Em desenvolvimento, mais permissivo
if os.getenv("ENVIRONMENT") == "production":
    # Production: Adiciona APITokenMiddleware
    app.add_middleware(APITokenMiddleware)
    print("Modo producao: API Token ativado")
else:
    # Development: Desativa APITokenMiddleware
    print("Modo desenvolvimento: API Token desativado")

app.add_middleware(InputValidationMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Inclui rotas
app.include_router(router)

# Serve arquivos estáticos (se necessário)
# app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))  # Render define PORT automaticamente
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Sem reload em produção
        log_level="info"
    )
