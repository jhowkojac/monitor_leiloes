"""Fontes mock para Detran MG, Detran SP e Superbid (dados de exemplo)."""
from datetime import datetime, timedelta
from typing import List

from app.models import Estado, FonteLeilao, VeiculoLeilao
from app.fontes.base import FonteLeilaoBase


def _gerar_id(fonte: str, i: int) -> str:
    return f"{fonte}_{i}"


def _imagens_placeholder(modelo: str) -> List[str]:
    base = "https://via.placeholder.com/400x250?text="
    # Espaços serão tratados pelo navegador como %20 automaticamente
    return [
        f"{base}{modelo}+1",
        f"{base}{modelo}+2",
        f"{base}{modelo}+3",
    ]


class FonteDetranMG(FonteLeilaoBase):
    """Leilões do Detran MG (dados de exemplo)."""

    @property
    def nome(self) -> str:
        return "Detran MG"

    async def listar_leiloes(self) -> List[VeiculoLeilao]:
        base = datetime.now()
        return [
            VeiculoLeilao(
                id=_gerar_id("detran_mg", 1),
                titulo="Fiat Uno 2015 - Belo Horizonte",
                placa="ABC1D23",
                marca="Fiat",
                modelo="Uno",
                ano=2015,
                valor_inicial=15000.0,
                valor_atual=15200.0,
                data_leilao=base + timedelta(days=7),
                estado=Estado.MG,
                cidade="Belo Horizonte",
                fonte=FonteLeilao.DETRAN_MG,
                url="https://www.detran.mg.gov.br/leiloes?lote=uno2015",
                imagem_url="https://via.placeholder.com/400x250?text=Fiat+Uno",
                imagens=_imagens_placeholder("Fiat+Uno"),
            ),
            VeiculoLeilao(
                id=_gerar_id("detran_mg", 2),
                titulo="Volkswagen Gol 2018 - Uberlândia",
                placa="XYZ9K87",
                marca="Volkswagen",
                modelo="Gol",
                ano=2018,
                valor_inicial=28000.0,
                valor_atual=28000.0,
                data_leilao=base + timedelta(days=14),
                estado=Estado.MG,
                cidade="Uberlândia",
                fonte=FonteLeilao.DETRAN_MG,
                url="https://www.detran.mg.gov.br/leiloes?lote=gol2018",
                imagem_url="https://via.placeholder.com/400x250?text=VW+Gol",
                imagens=_imagens_placeholder("VW+Gol"),
            ),
            VeiculoLeilao(
                id=_gerar_id("detran_mg", 3),
                titulo="Chevrolet Onix 2020 - Juiz de Fora",
                marca="Chevrolet",
                modelo="Onix",
                ano=2020,
                valor_inicial=45000.0,
                data_leilao=base + timedelta(days=21),
                estado=Estado.MG,
                cidade="Juiz de Fora",
                fonte=FonteLeilao.DETRAN_MG,
                url="https://www.detran.mg.gov.br/leiloes?lote=onix2020",
                imagem_url="https://via.placeholder.com/400x250?text=Onix",
                imagens=_imagens_placeholder("Onix"),
            ),
        ]


class FonteDetranSP(FonteLeilaoBase):
    """Leilões do Detran SP (dados de exemplo)."""

    @property
    def nome(self) -> str:
        return "Detran SP"

    async def listar_leiloes(self) -> List[VeiculoLeilao]:
        base = datetime.now()
        return [
            VeiculoLeilao(
                id=_gerar_id("detran_sp", 1),
                titulo="Honda Civic 2019 - São Paulo",
                placa="DEF4G56",
                marca="Honda",
                modelo="Civic",
                ano=2019,
                valor_inicial=95000.0,
                valor_atual=97800.0,
                data_leilao=base + timedelta(days=5),
                estado=Estado.SP,
                cidade="São Paulo",
                fonte=FonteLeilao.DETRAN_SP,
                url="https://www.detran.sp.gov.br/leiloes?lote=civic2019",
                imagem_url="https://via.placeholder.com/400x250?text=Civic",
                imagens=_imagens_placeholder("Civic"),
            ),
            VeiculoLeilao(
                id=_gerar_id("detran_sp", 2),
                titulo="Toyota Corolla 2021 - Campinas",
                marca="Toyota",
                modelo="Corolla",
                ano=2021,
                valor_inicial=120000.0,
                data_leilao=base + timedelta(days=12),
                estado=Estado.SP,
                cidade="Campinas",
                fonte=FonteLeilao.DETRAN_SP,
                url="https://www.detran.sp.gov.br/leiloes?lote=corolla2021",
                imagem_url="https://via.placeholder.com/400x250?text=Corolla",
                imagens=_imagens_placeholder("Corolla"),
            ),
            VeiculoLeilao(
                id=_gerar_id("detran_sp", 3),
                titulo="Hyundai HB20 2017 - Santos",
                marca="Hyundai",
                modelo="HB20",
                ano=2017,
                valor_inicial=42000.0,
                valor_atual=43500.0,
                data_leilao=base + timedelta(days=3),
                estado=Estado.SP,
                cidade="Santos",
                fonte=FonteLeilao.DETRAN_SP,
                url="https://www.detran.sp.gov.br/leiloes?lote=hb202017",
                imagem_url="https://via.placeholder.com/400x250?text=HB20",
                imagens=_imagens_placeholder("HB20"),
            ),
        ]


class FonteSuperbid(FonteLeilaoBase):
    """Leilões Superbid (MG/SP - dados de exemplo)."""

    @property
    def nome(self) -> str:
        return "Superbid"

    async def listar_leiloes(self) -> List[VeiculoLeilao]:
        base = datetime.now()
        return [
            VeiculoLeilao(
                id=_gerar_id("superbid", 1),
                titulo="Jeep Compass 2022 - Leilão Superbid SP",
                marca="Jeep",
                modelo="Compass",
                ano=2022,
                valor_inicial=110000.0,
                data_leilao=base + timedelta(days=10),
                estado=Estado.SP,
                cidade="São Paulo",
                fonte=FonteLeilao.SUPERBID,
                url="https://www.superbid.net/leilao/compass-2022",
                imagem_url="https://via.placeholder.com/400x250?text=Compass",
                imagens=_imagens_placeholder("Compass"),
            ),
            VeiculoLeilao(
                id=_gerar_id("superbid", 2),
                titulo="Renault Kwid 2020 - Leilão Superbid MG",
                marca="Renault",
                modelo="Kwid",
                ano=2020,
                valor_inicial=38000.0,
                data_leilao=base + timedelta(days=8),
                estado=Estado.MG,
                cidade="Belo Horizonte",
                fonte=FonteLeilao.SUPERBID,
                url="https://www.superbid.net/leilao/kwid-2020",
                imagem_url="https://via.placeholder.com/400x250?text=Kwid",
                imagens=_imagens_placeholder("Kwid"),
            ),
        ]


fonte_detran_mg = FonteDetranMG()
fonte_detran_sp = FonteDetranSP()
fonte_superbid = FonteSuperbid()
