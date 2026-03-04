"""Monitor de Leilões - FastAPI Application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import router
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
    print("🚀 Monitor de Leilões iniciando...")
    print("📊 Serviços de leilões configurados")
    print("🔒 Segurança configurada")
    yield
    # Shutdown
    print("🛑 Monitor de Leilões encerrando...")


app = FastAPI(
    title="Monitor de Leilões",
    description="API para monitoramento de leilões de veículos",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configura middlewares de segurança (em ordem inversa de execução)
app.add_middleware(APITokenMiddleware, protected_paths=["/api/leiloes/atualizar"])
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
