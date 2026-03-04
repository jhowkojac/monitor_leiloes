"""Fonte oficial do sistema de leilões do Detran MG.

IMPORTANTE: este conector depende da estrutura HTML atual do site
`https://leilao.detran.mg.gov.br/`. Caso o layout mude, pode ser
necessário ajustar os seletores de HTML abaixo.
"""
from __future__ import annotations

from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
import re

from app.fontes.base import FonteLeilaoBase
from app.models import Estado, FonteLeilao, VeiculoLeilao


BASE_URL = "https://leilao.detran.mg.gov.br/"
# Para evitar deixar a página muito lenta, limitamos quantos editais
# serão varridos a cada atualização.
MAX_EDITAIS = 5


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

            # Heurística: procurar todos os links "Detalhes" de editais
            count = 0
            for link in soup.find_all("a"):
                texto = (link.get_text() or "").strip().lower()
                if "detalhes" not in texto:
                    continue
                href = link.get("href")
                if not href:
                    continue
                edital_url = urljoin(BASE_URL, href)

                # Tenta extrair informações do bloco que contém o link
                bloco = link.find_parent(["div", "article", "tr", "li"]) or link
                bloco_texto = bloco.get_text(" ", strip=True)

                # Ex.: "Edital de Leilão 1445/2026 novo cruzeiro ..."
                codigo_match = re.search(r"\d{3,5}/\d{4}", bloco_texto)
                codigo = codigo_match.group(0) if codigo_match else "Edital"

                # Cidade (heurística): pega 1–2 palavras logo após o código
                cidade = None
                if codigo_match:
                    after = bloco_texto[codigo_match.end() :].strip()
                    partes = after.split()
                    if partes:
                        cidade = " ".join(partes[:2]).strip()

                titulo = f"Edital {codigo}"
                if cidade:
                    titulo = f"{titulo} - {cidade}"
                descricao = bloco_texto

                veiculos.append(
                    VeiculoLeilao(
                        id=f"detran_mg_edital_{codigo}_{count}",
                        titulo=titulo,
                        descricao=descricao,
                        estado=Estado.MG,
                        cidade=cidade,
                        fonte=FonteLeilao.DETRAN_MG,
                        url=edital_url,
                        imagem_url="https://via.placeholder.com/400x250?text=Edital+Detran+MG",
                        imagens=[
                            "https://via.placeholder.com/400x250?text=Edital+Detran+MG+1",
                            "https://via.placeholder.com/400x250?text=Edital+Detran+MG+2",
                        ],
                    )
                )
                count += 1
                if count >= MAX_EDITAIS:
                    break

        return veiculos

    async def listar_veiculos_do_edital(self, edital_url: str) -> List[VeiculoLeilao]:
        """Lista veículos de um edital específico do Detran MG.

        Esta leitura é feita sob demanda (ao abrir o edital na aplicação),
        para não deixar a atualização geral muito lenta.
        """
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(edital_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            resultado: List[VeiculoLeilao] = []

            # Tenta pegar o título/cidade do edital em algum cabeçalho
            titulo_edital = None
            cabecalho = soup.find(["h1", "h2", "h3"], string=True)
            if cabecalho:
                titulo_edital = cabecalho.get_text(strip=True)

            tabelas = soup.find_all("table")
            if not tabelas:
                return []

            tabela = tabelas[0]
            linhas = tabela.find_all("tr")

            for idx, tr in enumerate(linhas):
                # Ignorar cabeçalhos
                if tr.find("th"):
                    continue

                colunas = [td.get_text(strip=True) for td in tr.find_all("td")]
                if not colunas:
                    continue

                # Tenta achar link de foto, se existir
                foto_link = tr.find(
                    "a",
                    string=lambda t: t and "foto" in t.lower(),
                ) or tr.find(
                    "a",
                    href=lambda h: h and "foto" in (h or "").lower(),
                )
                imagem_url: Optional[str] = None
                imagens: Optional[List[str]] = None
                if foto_link and foto_link.get("href"):
                    imagem_url = urljoin(edital_url, foto_link["href"])
                    imagens = [imagem_url]

                titulo = colunas[0] or (titulo_edital or "Veículo em leilão")
                descricao = " | ".join(colunas[1:]) if len(colunas) > 1 else None

                veiculo = VeiculoLeilao(
                    id=f"detran_mg_edital_veiculo_{idx}_{abs(hash(edital_url))}",
                    titulo=titulo,
                    descricao=descricao,
                    estado=Estado.MG,
                    cidade=None,
                    fonte=FonteLeilao.DETRAN_MG,
                    url=edital_url,
                    imagem_url=imagem_url,
                    imagens=imagens,
                )
                resultado.append(veiculo)

            return resultado


fonte_detran_mg_oficial = FonteDetranMGOficial()
