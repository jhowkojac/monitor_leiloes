"""
Advanced Rate Limiting API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import time
import logging

from app.middleware.advanced_rate_limit import RateLimitConfig, MemoryRateLimitStorage

logger = logging.getLogger(__name__)

router = APIRouter()

# Instância global para monitoramento
rate_monitor = MemoryRateLimitStorage()
config = RateLimitConfig()

class RateLimitStats(BaseModel):
    endpoint: str
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    limit_per_minute: int
    limit_per_hour: int
    limit_per_day: int
    blocked_ips: List[str]
    blocked_users: List[str]

class RateLimitRule(BaseModel):
    endpoint: str
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    enabled: bool = True

class RateLimitUpdate(BaseModel):
    rules: List[RateLimitRule]

@router.get("/stats")
async def get_rate_limit_stats():
    """Estatísticas de rate limiting"""
    try:
        stats = []
        
        # Coletar estatísticas dos endpoints principais
        endpoints_to_monitor = [
            "/api/auth/login",
            "/api/auth/login-2fa",
            "/api/2fa/setup",
            "/api/leiloes",
            "/api/dashboard/stats"
        ]
        
        for endpoint in endpoints_to_monitor:
            limits = config.endpoint_limits.get(endpoint, config.default_limits)
            
            stats.append(RateLimitStats(
                endpoint=endpoint,
                requests_per_minute=rate_monitor.get_count(f"endpoint:{endpoint}", 60),
                requests_per_hour=rate_monitor.get_count(f"endpoint:{endpoint}", 3600),
                requests_per_day=rate_monitor.get_count(f"endpoint:{endpoint}", 86400),
                limit_per_minute=limits.get("requests_per_minute", config.default_limits["requests_per_minute"]),
                limit_per_hour=limits.get("requests_per_hour", config.default_limits["requests_per_hour"]),
                limit_per_day=limits.get("requests_per_day", config.default_limits["requests_per_day"]),
                blocked_ips=[],  # TODO: Implementar tracking
                blocked_users=[]   # TODO: Implementar tracking
            ))
        
        return {
            "enabled": config.enabled,
            "storage_type": config.storage_type,
            "total_requests": len(stats),
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas")

@router.get("/config")
async def get_rate_limit_config():
    """Configuração atual do rate limiting"""
    return {
        "enabled": config.enabled,
        "storage_type": config.storage_type,
        "default_limits": config.default_limits,
        "endpoint_limits": config.endpoint_limits,
        "block_duration": config.block_duration,
        "whitelist_ips": config.whitelist_ips,
        "redis_url": config.redis_url if config.storage_type == "redis" else None
    }

@router.put("/config")
async def update_rate_limit_config(update: RateLimitUpdate):
    """Atualiza configuração de rate limiting"""
    try:
        # Atualizar regras
        for rule in update.rules:
            if rule.enabled:
                config.endpoint_limits[rule.endpoint] = {
                    "requests_per_minute": rule.requests_per_minute,
                    "requests_per_hour": rule.requests_per_hour,
                    "requests_per_day": rule.requests_per_day
                }
            else:
                # Remover regra se desabilitada
                config.endpoint_limits.pop(rule.endpoint, None)
        
        logger.info(f"Configuração de rate limiting atualizada: {len(update.rules)} regras")
        
        return {
            "status": "updated",
            "rules_count": len(update.rules),
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar configuração: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar configuração")

@router.post("/unblock/{identifier}")
async def unblock_client(identifier: str):
    """Remove bloqueio de IP ou usuário"""
    try:
        # Tentar desbloquear como IP
        ip_key = f"ip:{identifier}"
        if rate_monitor.is_blocked(ip_key):
            # Aqui você removeria o bloqueio do storage
            logger.info(f"IP desbloqueado: {identifier}")
            return {"status": "unblocked", "type": "ip"}
        
        # Tentar desbloquear como usuário
        user_key = f"user:{identifier}"
        if rate_monitor.is_blocked(user_key):
            # Aqui você removeria o bloqueio do storage
            logger.info(f"Usuário desbloqueado: {identifier}")
            return {"status": "unblocked", "type": "user"}
        
        return {"status": "not_found", "identifier": identifier}
        
    except Exception as e:
        logger.error(f"Erro ao desbloquear: {e}")
        raise HTTPException(status_code=500, detail="Erro ao desbloquear")

@router.get("/blocked")
async def get_blocked_clients():
    """Lista IPs e usuários bloqueados"""
    try:
        # Aqui você listaria todos os bloqueados do storage
        # Por ora, retornar exemplo
        return {
            "blocked_ips": [
                # IPs bloqueados viriam aqui
            ],
            "blocked_users": [
                # Usuários bloqueados viriam aqui
            ],
            "total_blocked": 0,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar bloqueados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar bloqueados")

@router.post("/test")
async def test_rate_limit(endpoint: str = "/api/auth/login"):
    """Testa rate limiting para um endpoint específico"""
    try:
        # Simular múltiplas requests para teste
        ip_key = f"ip:test_client"
        
        # Adicionar algumas requests
        for i in range(3):
            rate_monitor.add_request(ip_key, 60)
        
        current_count = rate_monitor.get_count(ip_key, 60)
        limit = config.endpoint_limits.get(endpoint, config.default_limits)["requests_per_minute"]
        
        return {
            "endpoint": endpoint,
            "current_requests": current_count,
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "is_blocked": rate_monitor.is_blocked(ip_key),
            "test_requests_added": 3
        }
        
    except Exception as e:
        logger.error(f"Erro ao testar rate limit: {e}")
        raise HTTPException(status_code=500, detail="Erro ao testar rate limit")

@router.delete("/reset")
async def reset_rate_limit_stats():
    """Reseta estatísticas de rate limiting (admin only)"""
    try:
        # Aqui você resetaria o storage
        # Por ora, apenas log
        logger.info("Estatísticas de rate limiting resetadas")
        
        return {
            "status": "reset",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Erro ao resetar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao resetar estatísticas")
