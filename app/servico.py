"""Serviço de agregação e cache de leilões."""
from typing import Dict, List, Optional

from app.models import Estado, FonteLeilao, VeiculoLeilao
from app.fontes import fonte_detran_mg_oficial


class ServicoLeiloes:
    """Agrega leilões de todas as fontes e mantém cache em memória."""

    def __init__(self):
        # Usa apenas a fonte oficial do Detran MG (sem dados mockados).
        self._fontes = [fonte_detran_mg_oficial]
        self._cache: List[VeiculoLeilao] = []
        self._por_id: Dict[str, VeiculoLeilao] = {}

    async def atualizar(self) -> List[VeiculoLeilao]:
        """Busca de todas as fontes e atualiza o cache."""
        todos: List[VeiculoLeilao] = []
        for fonte in self._fontes:
            try:
                itens = await fonte.listar_leiloes()
                todos.extend(itens)
            except Exception:
                # Em produção, registre o erro em algum logger
                continue
        self._cache = todos
        self._por_id = {v.id: v for v in todos}
        return todos

    def listar(
        self,
        estado: Optional[Estado] = None,
        fonte: Optional[str] = None,
        cidade: Optional[str] = None,
    ) -> List[VeiculoLeilao]:
        """Lista leilões (editais) do cache com filtros opcionais."""
        resultado = list(self._cache)
        if estado:
            resultado = [v for v in resultado if v.estado == estado]
        if fonte:
            resultado = [v for v in resultado if v.fonte.value == fonte]
        if cidade:
            cidade_lower = cidade.strip().lower()
            resultado = [
                v
                for v in resultado
                if v.cidade and cidade_lower in v.cidade.lower()
            ]
        return resultado

    def obter_por_id(self, id_: str) -> Optional[VeiculoLeilao]:
        """Retorna um edital pelo ID."""
        return self._por_id.get(id_)

    async def listar_veiculos_por_edital(self, id_: str) -> List[VeiculoLeilao]:
        """Lista veículos de um edital específico, quando suportado pela fonte."""
        edital = self._por_id.get(id_)
        if not edital or not edital.url:
            return []

        # Hoje apenas Detran MG oficial suporta detalhamento por edital.
        if edital.fonte != FonteLeilao.DETRAN_MG:
            return []

        return await fonte_detran_mg_oficial.listar_veiculos_do_edital(edital.url)


servico_leiloes = ServicoLeiloes()
