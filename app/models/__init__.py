from .user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Definição direta para evitar que o Python precise buscar em outros arquivos que importam 'models'
class Estado(str, Enum):
    MG = 'MG'
    SP = 'SP'

class FonteLeilao(str, Enum):
    DETRAN_MG = 'detran_mg'
    DETRAN_SP = 'detran_sp'
    SUPERBID = 'superbid'
    OUTROS = 'outros'

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

__all__ = ['User', 'Estado', 'FonteLeilao', 'VeiculoLeilao', 'LeilaoResumo']
