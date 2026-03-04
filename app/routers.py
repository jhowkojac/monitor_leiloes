"""Rotas da API e páginas web."""
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models import Estado, LeilaoResumo
from app.servico import servico_leiloes

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def pagina_inicial(request: Request):
    """Página principal com listagem de leilões (editais)."""
    leiloes = servico_leiloes.listar()
    resumos = [
        LeilaoResumo(
            id=v.id,
            titulo=v.titulo,
            valor_inicial=v.valor_inicial,
            valor_atual=v.valor_atual,
            data_leilao=v.data_leilao,
            estado=v.estado,
            cidade=v.cidade,
            fonte=v.fonte,
            url=v.url,
            imagem_url=v.imagem_url,
            imagens=v.imagens,
        )
        for v in leiloes
    ]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "leiloes": resumos},
    )


@router.get("/editais/{id_}", response_class=HTMLResponse)
async def pagina_edital(id_: str, request: Request):
    """Página de detalhes de um edital, com veículos em carrossel."""
    edital = servico_leiloes.obter_por_id(id_)
    if not edital:
        raise HTTPException(status_code=404, detail="Edital não encontrado")

    veiculos = await servico_leiloes.listar_veiculos_por_edital(id_)
    return templates.TemplateResponse(
        "edital.html",
        {
            "request": request,
            "edital": edital,
            "veiculos": veiculos,
        },
    )


@router.get("/api/leiloes")
async def api_listar_leiloes(
    estado: Optional[Estado] = None,
    fonte: Optional[str] = None,
    cidade: Optional[str] = None,
):
    """API: lista leilões com filtros opcionais."""
    itens = servico_leiloes.listar(estado=estado, fonte=fonte, cidade=cidade)
    return {"total": len(itens), "leiloes": itens}


@router.get("/api/leiloes/atualizar")
async def api_atualizar_leiloes():
    """API: dispara atualização das fontes (refresh)."""
    itens = await servico_leiloes.atualizar()
    return {"total": len(itens), "mensagem": "Leilões atualizados."}


@router.get("/api/leiloes/{id_}")
async def api_obter_leilao(id_: str):
    """API: detalhes de um leilão pelo ID."""
    item = servico_leiloes.obter_por_id(id_)
    if not item:
        raise HTTPException(status_code=404, detail="Leilão não encontrado")
    return item
