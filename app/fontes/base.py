"""Interface base para fontes de leilões."""
from abc import ABC, abstractmethod
from typing import List

from app.models import VeiculoLeilao


class FonteLeilaoBase(ABC):
    """Interface para qualquer fonte de leilões (Detran, Superbid, etc.)."""

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome exibido da fonte."""
        pass

    @abstractmethod
    async def listar_leiloes(self) -> List[VeiculoLeilao]:
        """Retorna a lista de veículos em leilão desta fonte."""
        pass
