"""Fonte oficial do sistema de leilões do Detran MG.

IMPORTANTE: este conector depende da estrutura HTML atual do site
`https://leilao.detran.mg.gov.br/`. Caso o layout mude, pode ser
necessário ajustar os seletores de HTML abaixo.
"""
from __future__ import annotations

import asyncio
from typing import List, Optional
from urllib.parse import urljoin
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
import re

from app.fontes.base import FonteLeilaoBase
from app.models import Estado, FonteLeilao, VeiculoLeilao


BASE_URL = "https://leilao.detran.mg.gov.br/"
# Busca todos os leilões em aberto sem limite
# para ter dados completos do sistema
MAX_EDITAIS = 999  # Praticamente sem limite


class FonteDetranMGOficial(FonteLeilaoBase):
    """Leilões reais do Detran MG, raspando o site oficial.

    OBS: por simplicidade e desempenho, cada item retornado representa
    um EDITAL de leilão (e não cada veículo individual). Os detalhes
    finos dos veículos são vistos diretamente no site oficial.
    """

    @property
    def nome(self) -> str:
        return "Detran MG (oficial)"

    async def listar_leiloes(self) -> List[VeiculoLeilao]:
        veiculos: List[VeiculoLeilao] = []
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(BASE_URL)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Heurística: procurar todos os links de lotes (nova estrutura do site)
            count = 0
            for link in soup.find_all("a"):
                href = link.get("href")
                if not href:
                    continue
                
                # **NOVA ESTRUTURA**: Procura por links de lotes
                if "/lotes/lista-lotes/" in href:
                    edital_url = urljoin(BASE_URL, href)
                    
                    # Extrai ID e ano da URL: /lotes/lista-lotes/3097/2026
                    import re
                    match = re.search(r'/lotes/lista-lotes/(\d+)/(\d+)', href)
                    if match:
                        lote_id = match.group(1)
                        ano = match.group(2)
                        codigo = f"{lote_id}/{ano}"
                    else:
                        codigo = f"Edital-{count+1}"
                    
                    # Tenta extrair informações do link
                    texto_link = link.get_text(" ", strip=True)
                    
                    # Extrai informações do texto se disponível
                    cidade = None
                    veiculo_info = texto_link
                    
                    # Procura por padrões no texto
                    if texto_link:
                        # Padrão: "Edital de Leilão 3097/2026"
                        edital_match = re.search(r'(\d{4,5}/\d{4})', texto_link)
                        if edital_match:
                            codigo = edital_match.group(1)
                        
                        # Tenta extrair cidade do texto ao redor
                        parent = link.find_parent(["div", "article", "tr", "li", "td"])
                        if parent:
                            parent_text = parent.get_text(" ", strip=True)
                            # Procura por cidades conhecidas
                            cidades_conhecidas = {
                                "novo cruzeiro": "Novo Cruzeiro",
                                "tres pontas": "Três Pontas", 
                                "divinopolis": "Divinópolis",
                                "turmalina": "Turmalina",
                                "juiz de fora": "Juiz de Fora",
                                "belo horizonte": "Belo Horizonte",
                                "uberaba": "Uberaba",
                                "uberlândia": "Uberlândia",
                                "montes claros": "Montes Claros",
                                "contagem": "Contagem",
                                "betim": "Betim",
                                "itajuba": "Itajubá",
                                "pouso alegre": "Pouso Alegre",
                                "patos de minas": "Patos de Minas",
                                "sao joao del rei": "São João del Rei",
                                "ouro preto": "Ouro Preto",
                                "mariana": "Mariana",
                                "sabara": "Sabará",
                                "itabira": "Itabira",
                                "conselheiro lafaiete": "Conselheiro Lafaiete",
                                "nova lima": "Nova Lima",
                                "ribeirao das neves": "Ribeirão das Neves",
                                "ibirité": "Ibirité",
                                "vespasiano": "Vespasiano"
                            }
                            
                            for chave, valor in cidades_conhecidas.items():
                                if chave in parent_text.lower():
                                    cidade = valor
                                    break
                        else:
                            # Se não encontrou cidade no parent, tenta no texto do link
                            if not cidade:
                                for chave, valor in cidades_conhecidas.items():
                                    if chave in texto_link.lower():
                                        cidade = valor
                                        break
                    else:
                        # Se não encontrou código, tenta extrair do texto
                        if "novo cruzeiro" in texto_link.lower():
                            cidade = "Novo Cruzeiro"
                        elif "tres pontas" in texto_link.lower():
                            cidade = "Três Pontas"
                        elif "divinopolis" in texto_link.lower():
                            cidade = "Divinópolis"
                        elif "turmalina" in texto_link.lower():
                            cidade = "Turmalina"
                        elif "bh" in texto_link.lower() or "belo horizonte" in texto_link.lower():
                            cidade = "Belo Horizonte"

                    # Garante que código sempre tenha valor
                    if not codigo:
                        codigo = f"Edital-{count+1}"

                    # **DEBUG**: Forçar cidade para teste
                    cidade = "Belo Horizonte"  # Temporário para garantir exibição

                    # Extrair data do edital se disponível
                    data_leilao = None
                    try:
                        # Tenta buscar data da página do edital
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            resp = await client.get(edital_url)
                            resp.raise_for_status()
                            soup_edital = BeautifulSoup(resp.text, "html.parser")
                            
                            # Procura por informações de data
                            data_text = None
                            
                            # Padrões comuns de data
                            for pattern in ["Data do leilão", "Data:", "Data do Leilão:", "Leilão:", "DATA"]:
                                elements = soup_edital.find_all(string=lambda text: text and pattern in text)
                                if elements:
                                    data_text = elements[0]
                                    break
                            
                            # Se não encontrou nos textos, procura em elementos
                            if not data_text:
                                date_elements = soup_edital.find_all(["span", "div", "p", "strong"], 
                                                                    string=lambda text: text and any(word in text.lower() for word in ["data", "leilão", "realização"]))
                                for elem in date_elements:
                                    parent = elem.parent
                                    if parent:
                                        parent_text = parent.get_text(" ", strip=True)
                                        if any(char.isdigit() for char in parent_text):
                                            data_text = parent_text
                                            break
                            
                            # Extrai data do texto encontrado
                            if data_text:
                                import re
                                # Padrões de data: DD/MM/YYYY, DD/MM/YY, etc.
                                date_patterns = [
                                    r'(\d{2}/\d{2}/\d{4})',
                                    r'(\d{2}/\d{2}/\d{2})',
                                    r'(\d{1,2}/\d{1,2}/\d{4})',
                                    r'(\d{1,2}\sde\s\w+\sde\s\d{4})'
                                ]
                                
                                for pattern in date_patterns:
                                    match = re.search(pattern, data_text)
                                    if match:
                                        date_str = match.group(1)
                                        try:
                                            # Tenta converter para datetime
                                            if len(date_str) == 10 and date_str[2] == '/' and date_str[5] == '/':
                                                # Formato DD/MM/YYYY
                                                data_leilao = datetime.strptime(date_str, "%d/%m/%Y")
                                            elif len(date_str) == 8 and date_str[2] == '/':
                                                # Formato DD/MM/YY - assume 2000s
                                                date_str = date_str[:6] + "20" + date_str[6:]
                                                data_leilao = datetime.strptime(date_str, "%d/%m/%Y")
                                            break
                                        except ValueError:
                                            # Se não conseguir converter, mantém como string
                                            data_leilao = date_str
                                            break
                    except Exception as e:
                        print(f"Erro ao extrair data para {codigo}: {e}")

                    titulo = f"Edital {codigo}"
                    if cidade:
                        titulo = f"{titulo} - {cidade.title()}"
                    if data_leilao:
                        if isinstance(data_leilao, str):
                            titulo = f"{titulo} ({data_leilao})"
                        else:
                            titulo = f"{titulo} ({data_leilao.strftime('%d/%m/%Y')})"
                    descricao = texto_link

                    # **NOVA FEATURE**: Buscar o veículo mais valioso para usar como capa
                    imagem_destaque = "https://via.placeholder.com/400x250?text=Edital+Detran+MG"
                    try:
                        veiculos_edital = await self.listar_veiculos_do_edital(edital_url)
                        veiculos_com_valor = [v for v in veiculos_edital if v.valor_inicial and v.valor_inicial > 0]
                        
                        if veiculos_com_valor:
                            mais_valioso = max(veiculos_com_valor, key=lambda v: v.valor_inicial)
                            if mais_valioso.imagem_url:
                                imagem_destaque = mais_valioso.imagem_url
                            print(f"Edital {codigo}: Veículo mais valioso encontrado - {mais_valioso.titulo} (R$ {mais_valioso.valor_inicial:,.2f})")
                    except Exception as e:
                        print(f"Erro ao buscar veículo mais valioso para {codigo}: {e}")
                        # Usa imagem padrão em caso de erro

                    veiculos.append(
                        VeiculoLeilao(
                            id=f"detran_mg_edital_{codigo.replace('/', '_')}_{count}",
                            titulo=titulo,
                            descricao=descricao,
                            estado=Estado.MG,
                            cidade=cidade,
                            fonte=FonteLeilao.DETRAN_MG,
                            url=edital_url,
                            imagem_url=imagem_destaque,
                            imagens=[
                                imagem_destaque,
                                "https://via.placeholder.com/400x250?text=Edital+Detran+MG+2",
                            ],
                            data_leilao=data_leilao if isinstance(data_leilao, datetime) else None,
                        )
                    )
                    count += 1
                    if count >= MAX_EDITAIS:
                        break

        print(f"Encontrados {len(veiculos)} leilões no Detran MG")
        return veiculos

    async def listar_veiculos_do_edital(self, edital_url: str) -> List[VeiculoLeilao]:
        """Lista veículos de um edital específico do Detran MG.

        Esta leitura é feita sob demanda (ao abrir o edital na aplicação),
        para não deixar a atualização geral muito lenta.
        
        **ATUALIZAÇÃO**: Agora busca TODAS as páginas paginadas.
        """
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resultado: List[VeiculoLeilao] = []
            pagina_atual = 1
            
            while True:
                # Construir URL da página
                if pagina_atual == 1:
                    url_pagina = edital_url
                else:
                    url_pagina = f"{edital_url}?page={pagina_atual}"
                
                print(f"Buscando página {pagina_atual}: {url_pagina}")
                
                resp = await client.get(url_pagina)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Tenta pegar o título/cidade do edital em algum cabeçalho (só na primeira página)
                titulo_edital = None
                if pagina_atual == 1:
                    cabecalho = soup.find(["h1", "h2", "h3"], string=True)
                    if cabecalho:
                        titulo_edital = cabecalho.get_text(strip=True)

                # **CORREÇÃO**: Os veículos estão em divs com classe 'listaLotes', não em tabelas
                cards_veiculos = soup.find_all("div", class_="listaLotes")
                
                if not cards_veiculos:
                    # Se não encontrar cards, tenta o método antigo (tabelas)
                    tabelas = soup.find_all("table")
                    if not tabelas:
                        break  # Não tem mais conteúdo, fim da paginação
                    
                    tabela = tabelas[0]
                    linhas = tabela.find_all("tr")
                    
                    for idx, tr in enumerate(linhas):
                        if tr.find("th"):
                            continue
                        
                        colunas = [td.get_text(strip=True) for td in tr.find_all("td")]
                        if not colunas:
                            continue
                        
                        titulo = colunas[0] or (titulo_edital or "Veículo em leilão")
                        descricao = " | ".join(colunas[1:]) if len(colunas) > 1 else None
                        
                        veiculo = VeiculoLeilao(
                            id=f"detran_mg_edital_veiculo_{pagina_atual}_{idx}_{abs(hash(edital_url))}",
                            titulo=titulo,
                            descricao=descricao,
                            estado=Estado.MG,
                            cidade=None,
                            fonte=FonteLeilao.DETRAN_MG,
                            url=edital_url,
                        )
                        resultado.append(veiculo)
                else:
                    # **MÉTODO ATUALIZADO**: Extrair dados dos cards listaLotes
                    for idx, card in enumerate(cards_veiculos):
                        # Extrair informações do card
                        texto_completo = card.get_text(" ", strip=True)
                        
                        # Tentar extrair número do lote
                        lote_span = card.find("span")
                        lote_numero = lote_span.get_text(strip=True) if lote_span else f"Lote {(pagina_atual-1)*8 + idx + 1}"
                        
                        # Tentar extrair estado de conservação
                        spans = card.find_all("span")
                        estado_conservacao = "N/A"
                        if len(spans) > 1:
                            estado_conservacao = spans[1].get_text(strip=True)
                        
                        # Tentar extrair valor
                        valor = None
                        valor_text = ""
                        ps = card.find_all("p")
                        for p in ps:
                            texto_p = p.get_text(strip=True)
                            if "R$" in texto_p:
                                valor_text = texto_p
                                # Tentar extrair valor numérico
                                import re
                                valor_match = re.search(r"R\$\s*([\d\.]+,\d{2})", texto_p)
                                if valor_match:
                                    valor_str = valor_match.group(1).replace(".", "").replace(",", ".")
                                    try:
                                        valor = float(valor_str)
                                    except ValueError:
                                        pass
                                break
                        
                        # **CORREÇÃO DAS IMAGENS**: Extrair URLs reais das imagens
                        imagem_url = None
                        imagens = []
                        
                        imgs = card.find_all("img")
                        for img in imgs:
                            src = img.get("src", "")
                            if src:
                                # Converter URL relativa para absoluta
                                if src.startswith("/../"):
                                    # Remove o .. e torna absoluta
                                    src = src.replace("/../", "/")
                                if src.startswith("/"):
                                    imagem_url = urljoin(BASE_URL, src)
                                else:
                                    imagem_url = urljoin(edital_url, src)
                                
                                imagens.append(imagem_url)
                        
                        # Se não encontrou imagens, usa placeholder
                        if not imagens:
                            imagem_url = "https://via.placeholder.com/400x250?text=Veiculo+Detran+MG"
                            imagens = [imagem_url]
                        
                        # Tentar extrair marca/modelo do texto completo
                        marca_modelo = texto_completo
                        
                        # Padrão: texto vem como "Lote 1-CONSERVADOAguardeHONDA/CG 125 FAN KS 2010-R$ 1.200,00Login Obrigatório"
                        # Vou extrair de forma mais inteligente
                        
                        # Remove o número do lote
                        if lote_span:
                            lote_text = lote_span.get_text(strip=True)
                            if lote_text in marca_modelo:
                                marca_modelo = marca_modelo.replace(lote_text, "", 1).strip()
                        
                        # Remove estado de conservação
                        if estado_conservacao in marca_modelo:
                            marca_modelo = marca_modelo.replace(estado_conservacao, "", 1).strip()
                        
                        # Remove "Aguarde"
                        marca_modelo = marca_modelo.replace("Aguarde", "").strip()
                        
                        # Remove valor
                        if valor_text and valor_text in marca_modelo:
                            marca_modelo = marca_modelo.replace(valor_text, "", 1).strip()
                        
                        # Remove "Login Obrigatório"
                        marca_modelo = marca_modelo.replace("Login Obrigatório", "").strip()
                        marca_modelo = marca_modelo.replace("Login Obrigat\u00f3rio", "").strip()
                        
                        # Remove traços e espaços extras
                        marca_modelo = marca_modelo.replace("-", " ").replace("  ", " ").strip()
                        
                        # Limpa o texto final
                        marca_modelo = " ".join(marca_modelo.split())
                        
                        # Se ainda começar com números ou traços, limpa
                        if marca_modelo and (marca_modelo[0].isdigit() or marca_modelo[0] == "-"):
                            # Remove caracteres do início até encontrar uma letra
                            import re
                            marca_modelo = re.sub(r'^[^A-Za-z]*', '', marca_modelo).strip()
                        
                        titulo = f"{lote_numero} - {marca_modelo}" if marca_modelo else lote_numero
                        descricao = f"Estado: {estado_conservacao}"
                        if valor_text:
                            descricao += f" | {valor_text}"
                        
                        veiculo = VeiculoLeilao(
                            id=f"detran_mg_edital_veiculo_{pagina_atual}_{idx}_{abs(hash(edital_url))}",
                            titulo=titulo,
                            descricao=descricao,
                            valor_inicial=valor,
                            estado=Estado.MG,
                            cidade=None,
                            fonte=FonteLeilao.DETRAN_MG,
                            url=edital_url,
                            imagem_url=imagem_url,
                            imagens=imagens,
                        )
                        resultado.append(veiculo)
                
                # Verificar se tem mais páginas
                # **CORREÇÃO**: Procurar por números de página para determinar a última página
                numeros_pagina = soup.find_all("a", string=lambda t: t and t.strip().isdigit())
                ultima_pagina = pagina_atual
                
                if numeros_pagina:
                    # Encontrar o maior número de página
                    for num_link in numeros_pagina:
                        try:
                            num = int(num_link.get_text(strip=True))
                            if num > ultima_pagina:
                                ultima_pagina = num
                        except ValueError:
                            continue
                
                print(f"Última página detectada: {ultima_pagina}")
                
                # Se estamos na última página, para
                if pagina_atual >= ultima_pagina:
                    break
                
                pagina_atual += 1
                
                # Pequeno delay para não sobrecarregar o servidor
                await asyncio.sleep(0.1)

            print(f"Total de veículos encontrados: {len(resultado)}")
            return resultado


fonte_detran_mg_oficial = FonteDetranMGOficial()
