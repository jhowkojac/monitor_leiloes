"""
Advanced Rate Limiting Middleware
"""
import time
import json
import asyncio
from typing import Dict, Optional, Any, Union
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Mapeamento de window names para segundos
WINDOW_SECONDS = {
    "requests_per_minute": 60,
    "requests_per_hour": 3600,
    "requests_per_day": 86400
}
from starlette.responses import Response
import logging
import hashlib
import os

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Configuração para rate limiting"""
    
    def __init__(self):
        # Configurações gerais
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.storage_type = os.getenv("RATE_LIMIT_STORAGE", "memory")  # memory, redis
        
        # Configurações por endpoint
        self.default_limits = {
            "requests_per_minute": 100,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        }
        
        # Limits específicos por endpoint
        self.endpoint_limits = {
            "/api/auth/login": {"requests_per_minute": 5, "requests_per_hour": 20},
            "/api/auth/login-2fa": {"requests_per_minute": 10, "requests_per_hour": 50},
            "/api/2fa/setup": {"requests_per_minute": 3, "requests_per_hour": 10},
            "/api/2fa/enable": {"requests_per_minute": 3, "requests_per_hour": 10},
            "/api/leiloes/atualizar": {"requests_per_minute": 2, "requests_per_hour": 10},
            "/api/pwa/send-notification": {"requests_per_minute": 1, "requests_per_hour": 5},
        }
        
        # Configurações Redis (se disponível)
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_prefix = "rate_limit:"
        
        # Configurações de bloqueio
        self.block_duration = int(os.getenv("RATE_LIMIT_BLOCK_DURATION", "300"))  # 5 minutos
        self.whitelist_ips = os.getenv("RATE_LIMIT_WHITELIST", "").split(",")

class MemoryRateLimitStorage:
    """Storage em memória para rate limiting"""
    
    def __init__(self):
        self.requests = defaultdict(lambda: defaultdict(deque))
        self.blocks = defaultdict(dict)
        
    def is_blocked(self, key: str) -> bool:
        """Verifica se está bloqueado"""
        block_info = self.blocks.get(key)
        if not block_info:
            return False
        
        return time.time() < block_info["until"]
    
    def block(self, key: str, duration: int):
        """Bloqueia por X segundos"""
        self.blocks[key] = {
            "until": time.time() + duration,
            "reason": "Rate limit exceeded"
        }
        logger.warning(f"Rate limit bloqueado: {key} por {duration}s")
    
    def clean_old_blocks(self):
        """Limpa bloqueios expirados"""
        current_time = time.time()
        expired_keys = [
            key for key, block_info in self.blocks.items()
            if block_info["until"] <= current_time
        ]
        
        for key in expired_keys:
            del self.blocks[key]
    
    def add_request(self, key: str, window: Union[int, str]):
        """Adiciona request à janela"""
        current_time = time.time()
        
        # Converter window para segundos se for string
        if isinstance(window, str):
            window_seconds = WINDOW_SECONDS.get(window, 60)
        else:
            window_seconds = window
            
        request_queue = self.requests[key][window_seconds]
        
        # Remove requests antigos da janela
        while request_queue and request_queue[0] <= current_time - window_seconds:
            request_queue.popleft()
        
        # Adiciona request atual
        request_queue.append(current_time)
        
        return len(request_queue)
    
    def get_count(self, key: str, window: Union[int, str]) -> int:
        """Obtém count na janela"""
        current_time = time.time()
        
        # Converter window para segundos se for string
        if isinstance(window, str):
            window_seconds = WINDOW_SECONDS.get(window, 60)
        else:
            window_seconds = window
            
        request_queue = self.requests[key][window_seconds]
        
        # Remove requests antigos
        while request_queue and request_queue[0] <= current_time - window_seconds:
            request_queue.popleft()
        
        return len(request_queue)

class AdvancedRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware avançado de rate limiting"""
    
    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        
        # Inicializa storage
        if self.config.storage_type == "redis":
            self.storage = RedisRateLimitStorage(self.config)
        else:
            self.storage = MemoryRateLimitStorage()
    
    async def dispatch(self, request: Request, call_next):
        """Processa request com rate limiting"""
        
        if not self.config.enabled:
            return await call_next(request)
        
        # Obter IP e User ID
        client_ip = self.get_client_ip(request)
        user_id = await self.get_user_id(request)
        
        # Verificar whitelist
        if client_ip in self.config.whitelist_ips:
            return await call_next(request)
        
        # Gerar keys para rate limiting
        ip_key = f"ip:{client_ip}"
        user_key = f"user:{user_id}" if user_id else None
        endpoint_key = f"endpoint:{request.url.path}"
        
        # Verificar bloqueios
        if self.storage.is_blocked(ip_key) or (user_key and self.storage.is_blocked(user_key)):
            return self.create_blocked_response("Rate limit exceeded. Try again later.")
        
        # Obter limits para o endpoint
        limits = self.config.endpoint_limits.get(
            request.url.path, 
            self.config.default_limits
        )
        
        # Verificar rate limits
        violations = []
        
        for window_name, limit_name in [
            ("requests_per_minute", "requests_per_minute"),
            ("requests_per_hour", "requests_per_hour"),
            ("requests_per_day", "requests_per_day")
        ]:
            limit = limits.get(limit_name, self.config.default_limits[limit_name])
            
            # Verificar por IP
            ip_count = self.storage.add_request(ip_key, window_name)
            if ip_count > limit:
                violations.append(f"IP: {ip_count}/{limit} per {window_name}")
                self.storage.block(ip_key, self.config.block_duration)
            
            # Verificar por usuário (se autenticado)
            if user_key:
                user_count = self.storage.add_request(user_key, window_name)
                if user_count > limit:
                    violations.append(f"User: {user_count}/{limit} per {window_name}")
                    self.storage.block(user_key, self.config.block_duration)
        
        # Limpar bloqueios antigos
        self.storage.clean_old_blocks()
        
        # Se houver violações, bloquear
        if violations:
            logger.warning(f"Rate limit violado: {client_ip} - {violations}")
            return self.create_blocked_response(
                f"Rate limit exceeded: {'; '.join(violations)}"
            )
        
        # Adicionar headers de rate limit
        response = await call_next(request)
        self.add_rate_limit_headers(response, limits, ip_key, user_key)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Obtém IP real do cliente"""
        # Tentar vários headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        x_forwarded = request.headers.get("X-Forwarded")
        
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        elif real_ip:
            return real_ip
        elif x_forwarded:
            return x_forwarded.split(",")[0].strip()
        else:
            return request.client.host if request.client else "unknown"
    
    async def get_user_id(self, request: Request) -> Optional[str]:
        """Obtém ID do usuário autenticado"""
        try:
            # Tentar obter do token JWT
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization[7:]
                # Aqui você decodificaria o token para obter user_id
                # Por ora, usar um hash do token como ID
                return hashlib.md5(token.encode()).hexdigest()[:16]
        except:
            pass
        
        return None
    
    def create_blocked_response(self, message: str) -> Response:
        """Cria response de bloqueio"""
        return Response(
            content=json.dumps({
                "error": "Rate limit exceeded",
                "message": message,
                "retry_after": self.config.block_duration
            }),
            status_code=429,
            headers={
                "Content-Type": "application/json",
                "Retry-After": str(self.config.block_duration)
            }
        )
    
    def add_rate_limit_headers(self, response: Response, limits: dict, ip_key: str, user_key: Optional[str]):
        """Adiciona headers informativos de rate limit"""
        headers = {}
        
        # Para cada janela, adicionar header
        for window_name, limit_name in [
            ("requests_per_minute", "requests_per_minute"),
            ("requests_per_hour", "requests_per_hour"),
            ("requests_per_day", "requests_per_day")
        ]:
            limit = limits.get(limit_name, self.config.default_limits[limit_name])
            
            # Count por IP
            ip_count = self.storage.get_count(ip_key, window_name)
            headers[f"X-RateLimit-Limit-{window_name}"] = str(limit)
            headers[f"X-RateLimit-Remaining-{window_name}"] = str(max(0, limit - ip_count))
            headers[f"X-RateLimit-Reset-{window_name}"] = str(int(time.time()) + WINDOW_SECONDS.get(window_name, 60))
            
            # Count por usuário (se autenticado)
            if user_key:
                user_count = self.storage.get_count(user_key, window_name)
                headers[f"X-RateLimit-User-Limit-{window_name}"] = str(limit)
                headers[f"X-RateLimit-User-Remaining-{window_name}"] = str(max(0, limit - user_count))
        
        # Adicionar headers à response
        for key, value in headers.items():
            response.headers[key] = value

class RedisRateLimitStorage:
    """Storage Redis para rate limiting (produção)"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        # Aqui você implementaria a conexão Redis
        # Por ora, usar fallback para memória
        self.memory_storage = MemoryRateLimitStorage()
        logger.info("Redis storage não implementado, usando memory storage")
    
    def is_blocked(self, key: str) -> bool:
        return self.memory_storage.is_blocked(key)
    
    def block(self, key: str, duration: int):
        self.memory_storage.block(key, duration)
    
    def clean_old_blocks(self):
        self.memory_storage.clean_old_blocks()
    
    def add_request(self, key: str, window: int) -> int:
        return self.memory_storage.add_request(key, window)
    
    def get_count(self, key: str, window: int) -> int:
        return self.memory_storage.get_count(key, window)
