from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações da aplicação
    """
    
    # Configurações básicas
    APP_NAME: str = "Monitor de Leilões"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configurações de segurança
    SECRET_KEY: str = "your-secret-key-change-in-production"
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


# Instância global das configurações
settings = Settings()
