"""
Configurações de segurança para o Monitor de Leilões
"""
import os
from typing import List


class SecurityConfig:
    """Configurações de segurança da aplicação"""
    
    # Rate Limiting
    RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "100"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # segundos
    
    # Tokens
    API_TOKEN = os.getenv("API_TOKEN", "change_this_in_production_2024")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_jwt_secret_in_production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS = ["*"]
    
    # Content Security Policy
    CSP_DIRECTIVES = {
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com",
        "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
        "font-src": "'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
        "img-src": "'self' data: https://leilao.detran.mg.gov.br https://via.placeholder.com",
        "connect-src": "'self' https://leilao.detran.mg.gov.br",
        "frame-ancestors": "'none'",
        "base-uri": "'self'",
        "form-action": "'self'"
    }
    
    # Headers de segurança
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    # Validação de entrada
    MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB
    ALLOWED_MIME_TYPES = [
        "text/html",
        "text/css",
        "text/javascript",
        "application/javascript",
        "application/json",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp"
    ]
    
    # Padrões maliciosos para bloquear
    MALICIOUS_PATTERNS = [
        # XSS
        "<script", "</script>", "javascript:", "vbscript:",
        "onload=", "onerror=", "onclick=", "onmouseover=",
        "eval(", "alert(", "confirm(", "prompt(",
        "document.cookie", "window.location", "document.write",
        
        # SQL Injection
        "union select", "drop table", "delete from", "insert into",
        "update set", "create table", "alter table",
        
        # Path Traversal
        "../", "..\\", "%2e%2e%2f", "%2e%2e%5c",
        
        # Command Injection
        "exec(", "system(", "shell_exec", "passthru",
        "eval(", "assert(", "preg_replace",
        
        # LFI/RFI
        "file://", "ftp://", "http://", "https://",
        "php://", "data://", "expect://"
    ]
    
    # Logging
    LOG_REQUESTS = os.getenv("LOG_REQUESTS", "true").lower() == "true"
    LOG_SENSITIVE_DATA = False  # Nunca logar dados sensíveis
    MASK_SENSITIVE_FIELDS = [
        "password", "token", "secret", "key", "auth",
        "cookie", "session", "csrf", "api_key"
    ]
    
    # Session/Cookie
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "strict")
    
    # Upload de arquivos
    UPLOAD_MAX_SIZE = int(os.getenv("UPLOAD_MAX_SIZE", "5242880"))  # 5MB
    UPLOAD_ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    
    # HTTPS
    FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"
    SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", "")
    SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", "")
    
    @classmethod
    def get_csp_header(cls) -> str:
        """Gera header CSP completo"""
        directives = []
        for directive, value in cls.CSP_DIRECTIVES.items():
            directives.append(f"{directive} {value}")
        return "; ".join(directives)
    
    @classmethod
    def is_allowed_origin(cls, origin: str) -> bool:
        """Verifica se origin é permitida"""
        return origin in cls.ALLOWED_ORIGINS or origin == "null"
    
    @classmethod
    def validate_file_upload(cls, filename: str, content_type: str, size: int) -> tuple[bool, str]:
        """Valida upload de arquivo"""
        # Verifica tamanho
        if size > cls.UPLOAD_MAX_SIZE:
            return False, "File too large"
        
        # Verifica extensão
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in cls.UPLOAD_ALLOWED_EXTENSIONS:
            return False, "File type not allowed"
        
        # Verifica MIME type
        if content_type not in cls.ALLOWED_MIME_TYPES:
            return False, "MIME type not allowed"
        
        return True, "Valid file"
    
    @classmethod
    def mask_sensitive_data(cls, data: str, field_name: str = "") -> str:
        """Mascara dados sensíveis para logs"""
        if not data:
            return ""
        
        # Verifica se é campo sensível
        field_lower = field_name.lower()
        if any(sensitive in field_lower for sensitive in cls.MASK_SENSITIVE_FIELDS):
            return "*" * min(len(data), 8)
        
        # Para outros dados, mantém primeiros e últimos caracteres
        if len(data) <= 4:
            return "*" * len(data)
        
        return data[:2] + "*" * (len(data) - 4) + data[-2:]


class Environment:
    """Configurações específicas por ambiente"""
    
    @staticmethod
    def is_development() -> bool:
        return os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    @staticmethod
    def is_production() -> bool:
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    @staticmethod
    def is_testing() -> bool:
        return os.getenv("ENVIRONMENT", "development").lower() == "testing"
    
    @staticmethod
    def get_config() -> SecurityConfig:
        """Retorna configuração baseada no ambiente"""
        if Environment.is_production():
            return ProductionSecurityConfig()
        elif Environment.is_testing():
            return TestingSecurityConfig()
        else:
            return DevelopmentSecurityConfig()


class DevelopmentSecurityConfig(SecurityConfig):
    """Configurações de desenvolvimento"""
    
    RATE_LIMIT_CALLS = 1000  # Mais liberal em desenvolvimento
    LOG_REQUESTS = True
    
    CSP_DIRECTIVES = {
        **SecurityConfig.CSP_DIRECTIVES,
        "script-src": "'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://fonts.googleapis.com",
        "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
    }


class ProductionSecurityConfig(SecurityConfig):
    """Configurações de produção"""
    
    RATE_LIMIT_CALLS = 50  # Mais restritivo em produção
    FORCE_HTTPS = True
    
    CSP_DIRECTIVES = {
        **SecurityConfig.CSP_DIRECTIVES,
        "script-src": "'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com",
        "style-src": "'self' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
    }


class TestingSecurityConfig(SecurityConfig):
    """Configurações de teste"""
    
    RATE_LIMIT_CALLS = 10000  # Sem limitação em testes
    LOG_REQUESTS = False
    
    CSP_DIRECTIVES = {
        **SecurityConfig.CSP_DIRECTIVES,
        "script-src": "'self' 'unsafe-inline' 'unsafe-eval'",
        "style-src": "'self' 'unsafe-inline'",
    }


# Configuração global
security_config = Environment.get_config()
