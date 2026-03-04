"""Fontes de dados de leilões (MG, SP e outros)."""
from .base import FonteLeilaoBase
from .mock_mg_sp import fonte_detran_mg, fonte_detran_sp, fonte_superbid
from .detran_mg_oficial import fonte_detran_mg_oficial

__all__ = [
    "FonteLeilaoBase",
    "fonte_detran_mg",
    "fonte_detran_mg_oficial",
    "fonte_detran_sp",
    "fonte_superbid",
]
