"""
Bot Protection Middleware - reCAPTCHA v3 Integration
"""
import httpx
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

class BotProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware para proteção contra bots usando reCAPTCHA v3"""
    
    def __init__(self, app, secret_key: str, min_score: float = 0.5):
        super().__init__(app)
        self.secret_key = secret_key
        self.min_score = min_score
        self.recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
        
    async def verify_recaptcha(self, token: str) -> Dict[str, Any]:
        """Verifica o token do reCAPTCHA v3"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.recaptcha_url,
                    data={
                        "secret": self.secret_key,
                        "response": token
                    }
                )
                result = response.json()
                logger.info(f"reCAPTCHA verification: {result}")
                return result
        except Exception as e:
            logger.error(f"Error verifying reCAPTCHA: {e}")
            return {"success": False, "error": str(e)}
    
    async def dispatch(self, request: Request, call_next):
        """Verifica reCAPTCHA para requests sensíveis"""
        
        # Paths que exigem proteção
        protected_paths = [
            "/api/auth/login",
            "/api/auth/login-2fa",
            "/api/auth/register",
            "/api/2fa/setup",
            "/api/2fa/enable"
        ]
        
        # Verificar se path precisa de proteção
        if request.url.path in protected_paths:
            # Para GET requests, apenas continua
            if request.method == "GET":
                return await call_next(request)
            
            # Para POST/PUT/DELETE, verifica reCAPTCHA
            if request.method in ["POST", "PUT", "DELETE"]:
                try:
                    # Tentar obter token do header ou body
                    recaptcha_token = None
                    
                    # Verificar header
                    if "X-recaptcha-token" in request.headers:
                        recaptcha_token = request.headers["X-recaptcha-token"]
                    
                    # Se não tiver no header, tentar do body (para form submissions)
                    if not recaptcha_token and request.method == "POST":
                        try:
                            body = await request.json()
                            recaptcha_token = body.get("recaptcha_token")
                        except:
                            # Se não for JSON, tentar form data
                            try:
                                form = await request.form()
                                recaptcha_token = form.get("recaptcha_token")
                            except:
                                pass
                    
                    # Se não tiver token, bloqueia
                    if not recaptcha_token:
                        logger.warning(f"No reCAPTCHA token for {request.url.path}")
                        raise HTTPException(
                            status_code=403,
                            detail="reCAPTCHA verification required"
                        )
                    
                    # Verificar token
                    result = await self.verify_recaptcha(recaptcha_token)
                    
                    if not result.get("success", False):
                        logger.warning(f"reCAPTCHA verification failed: {result}")
                        raise HTTPException(
                            status_code=403,
                            detail="Bot protection verification failed"
                        )
                    
                    # Verificar score
                    score = result.get("score", 0.0)
                    if score < self.min_score:
                        logger.warning(f"reCAPTCHA score too low: {score}")
                        raise HTTPException(
                            status_code=403,
                            detail="Bot protection - suspicious activity detected"
                        )
                    
                    logger.info(f"reCAPTCHA verified successfully - score: {score}")
                    
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Error in bot protection: {e}")
                    # Em caso de erro, permite (fail-safe)
                    pass
        
        return await call_next(request)
