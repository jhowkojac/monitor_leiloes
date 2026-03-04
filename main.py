"""Aplicação FastAPI - Monitor de Leilões de Veículos MG/SP."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação.

    A atualização pesada das fontes (Detran, etc.) é feita apenas quando o
    usuário clica em "Atualizar lista" (rota /api/leiloes/atualizar),
    evitando deixar o carregamento inicial da página lento.
    """
    yield
    # shutdown se necessário


app = FastAPI(
    title="Monitor de Leilões de Veículos",
    description="Monitoramento de leilões de veículos em Minas Gerais e São Paulo",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
