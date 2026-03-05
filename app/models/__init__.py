from .user import User

# Importar os models diretamente do arquivo models.py
try:
    from ..models import Estado, LeilaoResumo, VeiculoLeilao, FonteLeilao
except ImportError as e:
    print(f"Erro ao importar models: {e}")
    # Definir classes vazias para evitar erro
    class Estado:
        pass
    class LeilaoResumo:
        pass
    class VeiculoLeilao:
        pass
    class FonteLeilao:
        pass

__all__ = ['User', 'Estado', 'LeilaoResumo', 'VeiculoLeilao', 'FonteLeilao']
