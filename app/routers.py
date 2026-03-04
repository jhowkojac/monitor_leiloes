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


@router.get("/init", response_class=HTMLResponse)
async def inicializar_cache(request: Request):
    """Inicializa o cache com dados dos leilões."""
    try:
        print("🔄 Forçando atualização do cache...")
        await servico_leiloes.atualizar()
        
        # Verifica se tem dados
        leiloes = servico_leiloes.listar()
        
        if leiloes:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "leiloes": leiloes,
                    "total": len(leiloes),
                    "mensagem": f"✅ Cache atualizado com {len(leiloes)} leilões!"
                },
            )
        else:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "leiloes": [],
                    "total": 0,
                    "mensagem": "⚠️ Nenhum leilão encontrado. Tente novamente em alguns minutos."
                },
            )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "leiloes": [],
                "total": 0,
                "mensagem": f"❌ Erro ao atualizar: {str(e)}"
            },
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


@router.get("/veiculos/{veiculo_id}")
async def pagina_veiculo_detalhes(veiculo_id: str, request: Request):
    """Página de detalhes do veículo com fotos em alta resolução."""
    # Extrair ID real do veículo do Detran
    if veiculo_id.startswith('detran_mg_edital_veiculo_'):
        # Formato: detran_mg_edital_veiculo_{pagina}_{idx}_{hash}
        partes = veiculo_id.split('_')
        if len(partes) >= 5:
            detran_id = partes[-1]  # Última parte é o ID real
        else:
            detran_id = veiculo_id.split('_')[-1]
    else:
        detran_id = veiculo_id
    
    # Buscar dados completos do veículo diretamente
    from app.fontes.detran_mg_oficial import fonte_detran_mg_oficial
    
    # Buscar todos os leilões e encontrar o veículo
    leiloes = await fonte_detran_mg_oficial.listar_leiloes()
    veiculo_encontrado = None
    
    for leilao in leiloes:
        veiculos = await fonte_detran_mg_oficial.listar_veiculos_do_edital(leilao.url)
        for veiculo in veiculos:
            if veiculo.id == veiculo_id:
                veiculo_encontrado = veiculo
                break
        if veiculo_encontrado:
            break
    
    if not veiculo_encontrado:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    return templates.TemplateResponse(
        "veiculo_detalhes.html",
        {
            "request": request,
            "veiculo": veiculo_encontrado,
            "detran_id": detran_id,
        },
    )
