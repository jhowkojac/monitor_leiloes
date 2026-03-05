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


@router.get("/setup-2fa", response_class=HTMLResponse)
async def pagina_setup_2fa(request: Request):
    """Página de configuração de 2FA."""
    # Verificar se está logado
    user = get_current_user_optional(request)
    if not user:
        # Não está logado, redirecionar para login
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("setup_2fa.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def pagina_dashboard(request: Request):
    """Página do dashboard administrativo."""
    # Verificar se está logado
    user = get_current_user_optional(request)
    if not user:
        # Não está logado, redirecionar para login
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
    
    # Verificar se é admin
    if not user.get("is_admin", False):
        # Não é admin, redirecionar para página inicial
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("dashboard.html", {"request": request})


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


@router.get("/lote/{lote_id}")
async def pagina_lote_detalhes(lote_id: str, request: Request):
    """Página de detalhes do lote com design moderno e integração FIPE"""
    try:
        print(f"🔍 Buscando lote ID: {lote_id}")
        
        # Primeiro tenta encontrar no cache local
        leiloes_cache = servico_leiloes.listar()
        lote_encontrado = None
        edital_encontrado = None
        
        # Procura nos leilões em cache
        for leilao in leiloes_cache:
            if lote_id in leilao.id:
                print(f"✅ Lote encontrado no cache do edital: {leilao.titulo}")
                # Busca os veículos deste edital específico
                from app.fontes.detran_mg_oficial import fonte_detran_mg_oficial
                veiculos = await fonte_detran_mg_oficial.listar_veiculos_do_edital(leilao.url)
                
                for veiculo in veiculos:
                    if veiculo.id == lote_id:
                        lote_encontrado = veiculo
                        edital_encontrado = leilao
                        print(f"✅ Lote encontrado: {veiculo.titulo}")
                        break
                
                if lote_encontrado:
                    break
        
        # Se não encontrou, tenta busca mais ampla
        if not lote_encontrado:
            print(f"🔄 Busca ampla - tentando encontrar em todos os editais...")
            from app.fontes.detran_mg_oficial import fonte_detran_mg_oficial
            
            # Busca todos os leilões novamente
            todos_leiloes = await fonte_detran_mg_oficial.listar_leiloes()
            
            for leilao in todos_leiloes:
                if lote_id in leilao.id:
                    print(f"🔍 Verificando edital: {leilao.titulo}")
                    veiculos = await fonte_detran_mg_oficial.listar_veiculos_do_edital(leilao.url)
                    
                    for veiculo in veiculos:
                        if veiculo.id == lote_id:
                            lote_encontrado = veiculo
                            edital_encontrado = leilao
                            print(f"✅ Lote encontrado na busca ampla: {veiculo.titulo}")
                            break
                    
                    if lote_encontrado:
                        break
        
        if not lote_encontrado:
            print(f"❌ Lote não encontrado em nenhum edital")
            print(f"💡 Dicas: Verifique se o ID está correto ou se o lote ainda está disponível")
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        
        # Extrai informações para FIPE
        from app.servico_fipe import servico_fipe
        
        # Tenta extrair marca, modelo e ano do título
        titulo = lote_encontrado.titulo
        marca, modelo, ano = _extrair_dados_veiculo(titulo)
        
        # Busca valor FIPE
        valor_fipe = None
        if marca and modelo and ano:
            print(f"🔍 Buscando valor FIPE para: {marca} {modelo} {ano}")
            valor_fipe = await servico_fipe.buscar_valor_fipe(marca, modelo, ano)
            
            # Se falhar, tenta com mock
            if not valor_fipe:
                print(f"🔄 Usando valor FIPE mock para: {marca} {modelo} {ano}")
                valor_fipe = await servico_fipe.get_mock_fipe_value(marca, modelo, ano)
        else:
            print(f"🔄 Não foi possível extrair dados do título: {titulo}")
            valor_fipe = await servico_fipe.get_mock_fipe_value("Veículo", "Genérico", "2020")
        
        # Extrai o detran_id para o template
        detran_id = lote_id.replace("detran_mg_edital_veiculo_", "").split("_", 3)[-1]
        
        # Prepara dados adicionais
        dados_adicionais = _preparar_dados_adicionais(lote_encontrado, valor_fipe)
        
        return templates.TemplateResponse(
            "lote_detalhes.html",
            {
                "request": request,
                "lote": lote_encontrado,
                "edital": edital_encontrado,
                "lote_id": lote_id,
                "detran_id": detran_id,
                "valor_fipe": valor_fipe,
                "dados_adicionais": dados_adicionais,
            },
        )
        
    except HTTPException:
        # Repassa HTTP exceptions (como 404)
        raise
    except Exception as e:
        print(f"❌ Erro ao buscar lote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lote: {str(e)}")


def _extrair_dados_veiculo(titulo: str) -> tuple[str, str, str]:
    """
    Extrai marca, modelo e ano do título do veículo
    Retorna (marca, modelo, ano)
    """
    import re
    
    # Padrões comuns de títulos
    padroes = [
        # Ex: "VOLKSWAGEN/GOL 1.0 2012"
        r'^([A-ZÇÁÀÂÃÉÊÍÓÔÕÚÜÇÑ\s]+)/([A-Z0-9ÇÁÀÂÃÉÊÍÓÔÕÚÜÇÑ\s]+)\s+([\d]{4})',
        # Ex: "FIAT/PALIO 1.0 2015"
        r'^([A-ZÇÁÀÂÃÉÊÍÓÔÕÚÜÇÑ\s]+)/([A-Z0-9ÇÁÀÂÃÉÊÍÓÔÕÚÜÇÑ\s]+)\s+([\d]{4})',
        # Ex: "CHEVROLET ONIX 2018"
        r'^([A-ZÇÁÀÂÃÉÊÍÓÔÕÚÜÇÑ\s]+)\s+([A-Z0-9ÇÁÀÂÃÉÊÍÓÔÕÚÜÇÑ\s]+)\s+([\d]{4})',
    ]
    
    for padrao in padroes:
        match = re.search(padrao, titulo, re.IGNORECASE)
        if match:
            marca = match.group(1).strip()
            modelo = match.group(2).strip()
            ano = match.group(3).strip()
            return marca, modelo, ano
    
    # Se não encontrar padrão, tenta extrair ano
    ano_match = re.search(r'([\d]{4})', titulo)
    ano = ano_match.group(1) if ano_match else "2020"
    
    # Se não encontrar, retorna valores genéricos
    return "Veículo", "Genérico", ano


def _preparar_dados_adicionais(lote, valor_fipe) -> dict:
    """Prepara dados adicionais para exibição"""
    dados = {
        "valor_inicial": getattr(lote, 'valor_inicial', None),
        "valor_atual": getattr(lote, 'valor_atual', None),
        "marca": getattr(lote, 'marca', 'N/A'),
        "modelo": getattr(lote, 'modelo', 'N/A'),
        "cor": getattr(lote, 'cor', 'N/A'),
        "ano_modelo": getattr(lote, 'ano_modelo', 'N/A'),
        "ano_fabricacao": getattr(lote, 'ano_fabricacao', 'N/A'),
        "combustivel": getattr(lote, 'combustivel', 'N/A'),
        "condicao": getattr(lote, 'condicao', 'N/A'),
        "placa": getattr(lote, 'placa', 'N/A'),
        "renavam": getattr(lote, 'renavam', 'N/A'),
    }
    
    # Calcula margem se tiver valor FIPE
    if valor_fipe and dados["valor_inicial"]:
        try:
            # Remove formatação do valor FIPE
            valor_fipe_str = valor_fipe.get("valor", "R$ 0").replace("R$", "").replace(".", "").replace(",", ".").strip()
            valor_fipe_num = float(valor_fipe_str)
            
            margem = ((valor_fipe_num - dados["valor_inicial"]) / dados["valor_inicial"]) * 100
            dados["margem_lucro"] = round(margem, 2)
        except:
            dados["margem_lucro"] = None
    
    return dados
