"""Rotas da API e páginas web."""
from typing import Optional
import os
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models import Estado, LeilaoResumo, VeiculoLeilao, FonteLeilao
from app.models.user import User
from app.servico import servico_leiloes
from app.middleware.auth import get_current_user_optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    """Página de login."""
    # Verificar se já está logado
    user = get_current_user_optional(request)
    if user:
        # Já está logado, redirecionar para página inicial
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})


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
        {
            "request": request,
            "leiloes": resumos,
            "total": len(resumos),  # Adicionando a variável total
        },
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
            # Testa conexão rápida (sem asyncio.run - já estamos em contexto async)
            test_leiloes = await fonte_detran_mg_oficial.listar_leiloes()
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
    estado: Optional[str] = None,
    fonte: Optional[str] = None,
    cidade: Optional[str] = None,
):
    """API: lista leilões com filtros opcionais."""
    itens = servico_leiloes.listar(estado=Estado(estado) if estado else None, fonte=fonte, cidade=cidade)
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


@router.get("/health")
async def health_check():
    """Health check do sistema."""
    try:
        # Verifica cache
        leiloes = servico_leiloes.listar()
        
        # Testa conexão com Detran (rápido)
        from app.fontes.detran_mg_oficial import fonte_detran_mg_oficial
        conexao_status = "Desconhecido"
        
        try:
            # Teste rápido (sem await completo para não bloquear)
            import asyncio
            task = asyncio.create_task(fonte_detran_mg_oficial.listar_leiloes())
            await asyncio.wait_for(task, timeout=5.0)
            conexao_status = "✅ Funcionando"
        except asyncio.TimeoutError:
            conexao_status = "⚠️ Timeout (lento)"
        except Exception:
            conexao_status = "❌ Erro"
        
        health_data = {
            "status": "healthy" if leiloes else "degraded",
            "timestamp": datetime.now().isoformat(),
            "cache": {
                "status": "✅ OK" if leiloes else "❌ Vazio",
                "count": len(leiloes),
                "last_update": "recente" if leiloes else "nunca"
            },
            "conexao_detran": conexao_status,
            "endpoints": {
                "principal": "/",
                "api": "/api/leiloes",
                "debug": "/debug",
                "health": "/health",
                "docs": "/docs"
            },
            "features": {
                "cache_automatico": "✅ Ativo",
                "carregamento_automatico": "✅ Ativo",
                "busca_otimizada": "✅ Ativo",
                "debug_avancado": "✅ Ativo"
            }
        }
        
        return {
            "status_code": 200,
            "content": health_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "content": {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        }


@router.get("/veiculos/{veiculo_id}")
async def pagina_veiculo_detalhes(veiculo_id: str, request: Request):
    """Página de detalhes do veículo com fotos em alta resolução."""
    try:
        print(f"🔍 Buscando veículo ID: {veiculo_id}")
        
        # Primeiro tenta encontrar no cache local
        leiloes_cache = servico_leiloes.listar()
        veiculo_encontrado = None
        edital_encontrado = None
        
        # Procura nos leilões em cache
        for leilao in leiloes_cache:
            if veiculo_id in leilao.id:
                print(f"✅ Veículo encontrado no cache do edital: {leilao.titulo}")
                # Busca os veículos deste edital específico
                from app.fontes.detran_mg_oficial import fonte_detran_mg_oficial
                veiculos = await fonte_detran_mg_oficial.listar_veiculos_do_edital(leilao.url)
                
                for veiculo in veiculos:
                    if veiculo.id == veiculo_id:
                        veiculo_encontrado = veiculo
                        edital_encontrado = leilao
                        print(f"✅ Veículo encontrado: {veiculo.titulo}")
                        break
                
                if veiculo_encontrado:
                    break
        
        # Se não encontrou, tenta busca mais ampla
        if not veiculo_encontrado:
            print(f"🔄 Busca ampla - tentando encontrar em todos os editais...")
            from app.fontes.detran_mg_oficial import fonte_detran_mg_oficial
            
            # Busca todos os leilões novamente
            todos_leiloes = await fonte_detran_mg_oficial.listar_leiloes()
            
            for leilao in todos_leiloes:
                if veiculo_id in leilao.id:
                    print(f"🔍 Verificando edital: {leilao.titulo}")
                    veiculos = await fonte_detran_mg_oficial.listar_veiculos_do_edital(leilao.url)
                    
                    for veiculo in veiculos:
                        if veiculo.id == veiculo_id:
                            veiculo_encontrado = veiculo
                            edital_encontrado = leilao
                            print(f"✅ Veículo encontrado na busca ampla: {veiculo.titulo}")
                            break
                    
                    if veiculo_encontrado:
                        break
        
        if not veiculo_encontrado:
            print(f"❌ Veículo não encontrado em nenhum edital")
            print(f"💡 Dicas: Verifique se o ID está correto ou se o veículo ainda está disponível")
            raise HTTPException(status_code=404, detail="Veículo não encontrado")
        
        # Extrai o detran_id para o template
        detran_id = veiculo_id.replace("detran_mg_edital_veiculo_", "").split("_", 3)[-1]
        
        return templates.TemplateResponse(
            "veiculo_detalhes.html",
            {
                "request": request,
                "veiculo": veiculo_encontrado,
                "edital": edital_encontrado,
                "veiculo_id": veiculo_id,
                "detran_id": detran_id,
            },
        )
        
    except HTTPException:
        # Repassa HTTP exceptions (como 404)
        raise
    except Exception as e:
        print(f"❌ Erro ao buscar veículo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar veículo: {str(e)}")
