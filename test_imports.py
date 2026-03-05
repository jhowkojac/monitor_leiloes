# Import direto dos arquivos para evitar circular import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from models import Estado, LeilaoResumo, VeiculoLeilao, FonteLeilao
from models.user import User

print("Imports funcionando!")
print(f"Estado: {Estado}")
print(f"LeilaoResumo: {LeilaoResumo}")
print(f"User: {User}")
