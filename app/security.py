"""
Middleware de segurança para o Monitor de Leilões
"""
import time
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import hashlib
import hmac
from typing import Optional
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de segurança
        security_headers = {
            # Proteção contra XSS
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # Política de conteúdo (básica)
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https://leilao.detran.mg.gov.br https://via.placeholder.com; "
                "connect-src 'self' https://leilao.detran.mg.gov.br; "
                "frame-ancestors 'none';"
            ),
            
            # Outros headers
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting básico"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        # Pega IP do cliente
        client_ip = self._get_client_ip(request)
        
        # Verifica rate limit
        if not self._is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(self.period)}
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrai IP real do cliente"""
        # Headers comuns para proxies
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        elif real_ip:
            return real_ip
        else:
            return request.client.host
    
    def _is_allowed(self, client_ip: str) -> bool:
        """Verifica se o cliente pode fazer a requisição"""
        now = time.time()
        
        # Limpa clientes antigos
        self.clients = {
            ip: (count, timestamp) 
            for ip, (count, timestamp) in self.clients.items() 
            if now - timestamp < self.period
        }
        
        # Verifica se o cliente existe
        if client_ip in self.clients:
            count, timestamp = self.clients[client_ip]
            if now - timestamp < self.period:
                if count >= self.calls:
                    return False
                self.clients[client_ip] = (count + 1, timestamp)
                return True
        
        # Novo cliente ou reset
        self.clients[client_ip] = (1, now)
        return True


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições (sem dados sensíveis)"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição (sem dados sensíveis)
        self._log_request(request)
        
        response = await call_next(request)
        
        # Log da resposta
        process_time = time.time() - start_time
        self._log_response(request, response, process_time)
        
        return response
    
    def _log_request(self, request: Request):
        """Log da requisição (sem dados sensíveis)"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
              f"{request.method} {request.url.path} "
              f"from {self._get_client_ip(request)}")
    
    def _log_response(self, request: Request, response: Response, process_time: float):
        """Log da resposta"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
              f"{request.method} {request.url.path} "
              f"-> {response.status_code} "
              f"in {process_time:.3f}s")
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrai IP do cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        elif real_ip:
            return real_ip
        else:
            return request.client.host


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware para validação básica de entrada"""
    
    async def dispatch(self, request: Request, call_next):
        # Validação básica de URL
        if self._has_malicious_patterns(request.url.path):
            raise HTTPException(status_code=400, detail="Invalid request")
        
        # Validação de headers
        for header_name, header_value in request.headers.items():
            if self._has_malicious_patterns(header_value):
                raise HTTPException(status_code=400, detail="Invalid header")
        
        response = await call_next(request)
        return response
    
    def _has_malicious_patterns(self, text: str) -> bool:
        """Verifica padrões maliciosos básicos"""
        malicious_patterns = [
            "<script", "</script>", "javascript:", "vbscript:",
            "onload=", "onerror=", "onclick=", "onmouseover=",
            "eval(", "alert(", "confirm(", "prompt(",
            "document.cookie", "window.location", "document.write",
            "../", "..\\", "%2e%2e%2f", "%2e%2e%5c",
            "union select", "drop table", "delete from", "insert into",
            "exec(", "system(", "shell_exec", "passthru"
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in malicious_patterns)


class APITokenMiddleware(BaseHTTPMiddleware):
    """Middleware para proteção de APIs com token simples"""
    
    def __init__(self, app, protected_paths: list = None):
        super().__init__(app)
        self.protected_paths = protected_paths or ["/api/leiloes/atualizar"]
        self.api_token = os.getenv("API_TOKEN", "default_token_change_in_production")
    
    async def dispatch(self, request: Request, call_next):
        # Verifica se a rota precisa de proteção
        if any(request.url.path.startswith(path) for path in self.protected_paths):
            token = request.headers.get("Authorization")
            if not token or not self._validate_token(token):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or missing API token"
                )
        
        response = await call_next(request)
        return response
    
    def _validate_token(self, token: str) -> bool:
        """Valida token da API"""
        # Remove "Bearer " se presente
        if token.startswith("Bearer "):
            token = token[7:]
        
        # Compara com token esperado
        return hmac.compare_digest(token, self.api_token)


# Classe para segurança de dados
class SecurityUtils:
    """Utilitários de segurança"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash de senha (para uso futuro)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitização básica de entrada"""
        if not text:
            return ""
        
        # Remove caracteres perigosos
        dangerous_chars = ["<", ">", "&", '"', "'", "/", "\\", "(", ")", "{", "}"]
        for char in dangerous_chars:
            text = text.replace(char, "")
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validação básica de e-mail"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validação básica de telefone"""
        import re
        # Remove caracteres não numéricos
        clean_phone = re.sub(r'[^\d]', '', phone)
        # Telefone brasileiro: 10 ou 11 dígitos
        return len(clean_phone) in [10, 11]
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
        """Mascara dados sensíveis para logs"""
        if not data or len(data) < 4:
            return mask_char * len(data) if data else ""
        
        # Mantém primeiros 2 e últimos 2 caracteres
        return data[:2] + mask_char * (len(data) - 4) + data[-2:]
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Gera token CSRF simples"""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(token: str, expected_token: str) -> bool:
        """Valida token CSRF"""
        return hmac.compare_digest(token, expected_token)
