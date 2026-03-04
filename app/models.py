"""Modelos de dados para leilões."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Estado(str, Enum):
    """Estados com foco do monitoramento."""
    MG = "MG"
    SP = "SP"


class FonteLeilao(str, Enum):
    """Fontes de leilões suportadas."""
    DETRAN_MG = "detran_mg"
    DETRAN_SP = "detran_sp"
    SUPERBID = "superbid"
    OUTROS = "outros"


class VeiculoLeilao(BaseModel):
    """Dados de um veículo em leilão."""
    id: str
    titulo: str
    descricao: Optional[str] = None
    placa: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    valor_inicial: Optional[float] = None
    valor_atual: Optional[float] = None
    data_leilao: Optional[datetime] = None
    estado: Estado
    cidade: Optional[str] = None
    fonte: FonteLeilao
    url: Optional[str] = None
    imagem_url: Optional[str] = None
    imagens: Optional[List[str]] = None
    atualizado_em: datetime = Field(default_factory=datetime.now)


class LeilaoResumo(BaseModel):
    """Resumo de leilão para listagem."""
    id: str
    titulo: str
    valor_inicial: Optional[float] = None
    valor_atual: Optional[float] = None
    data_leilao: Optional[datetime] = None
    estado: Estado
    cidade: Optional[str] = None
    fonte: FonteLeilao
    url: Optional[str] = None
    imagem_url: Optional[str] = None
    imagens: Optional[List[str]] = None
