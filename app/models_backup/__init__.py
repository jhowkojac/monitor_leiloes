from .user import User

# Importar models com path absoluto para evitar circular import
import sys
import os

# Obter o path absoluto do diretório raiz do app
app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_root)

# Importar models do arquivo models.py
from models import Estado, LeilaoResumo, VeiculoLeilao, FonteLeilao

__all__ = ['User', 'Estado', 'LeilaoResumo', 'VeiculoLeilao', 'FonteLeilao']
