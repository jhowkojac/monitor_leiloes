"""Rotas da API e páginas web."""
from typing import Optional
import os
from datetime import datetime

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


@router.get("/debug", response_class=HTMLResponse)
async def debug_info(request: Request):
    """Endpoint de debug para verificar status do sistema."""
    try:
        # Verifica cache
        leiloes = servico_leiloes.listar()
        
        # Testa conexão com Detran
        from app.fontes.detran_mg_oficial import fonte_detran_mg_oficial
        test_conexao = "Desconhecido"
        
        try:
            import asyncio
            # Testa conexão rápida
            test_leiloes = asyncio.run(fonte_detran_mg_oficial.listar_leiloes())
            if test_leiloes:
                test_conexao = "✅ Funcionando"
            else:
                test_conexao = "❌ Sem dados"
        except Exception as e:
            test_conexao = f"❌ Erro: {str(e)[:50]}"
        
        debug_info = {
            "cache_status": f"✅ {len(leiloes)} leilões no cache" if leiloes else "❌ Cache vazio",
            "conexao_detran": test_conexao,
            "ambiente": os.getenv("ENVIRONMENT", "development"),
            "rate_limit": os.getenv("RATE_LIMIT_CALLS", "100"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "endpoints_disponiveis": [
                "/ - Página principal",
                "/init - Forçar atualização",
                "/debug - Informações de debug",
                "/api/leiloes - API de leilões",
                "/docs - Documentação"
            ]
        }
        
        return templates.TemplateResponse(
            "debug.html",
            {
                "request": request,
                "debug_info": debug_info,
                "leiloes": leiloes[:5],  # Primeiros 5 para debug
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "debug.html",
            {
                "request": request,
                "erro": f"Erro no debug: {str(e)}",
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
