from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Configurações da aplicação
    """
    
    # Configurações básicas
    APP_NAME: str = "Monitor de Leilões"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configurações de segurança - SEM DEFAULTS por segurança
    SECRET_KEY: str = None  # Deve vir de variável de ambiente
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Configurações do banco
    DATABASE_URL: str = "sqlite:///./monitor_leiloes.db"
    
    # Configurações CORS
    ALLOWED_ORIGINS: list = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validação crítica: SECRET_KEY é obrigatório
        if not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY não está definido. "
                "Defina a variável de ambiente SECRET_KEY antes de iniciar a aplicação. "
                "Em desenvolvimento, crie um arquivo .env com: SECRET_KEY=seu-secret-aqui"
            )


# Instância global das configurações
try:
    settings = Settings()
except ValueError as e:
    print(f"ERRO DE CONFIGURAÇÃO: {e}")
    raise
