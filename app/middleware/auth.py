from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.services.jwt import jwt_service
from app.services.user import user_service
from app.database import get_db
from functools import wraps
from typing import Optional


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware para autenticação JWT
    """
    
    async def dispatch(self, request: Request, call_next):
        # Rotas que não precisam de autenticação
        public_paths = [
            "/",
            "/login",
            "/static",
            "/api/auth/login",
            "/api/auth/refresh",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        # Verificar se a rota é pública
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Verificar token de autenticação
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                content='{"detail": "Not authenticated"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            )
        
        token = auth_header.split(" ")[1]
        
        # Verificar token
        user_data = jwt_service.get_user_from_token(token)
        
        if not user_data:
            return Response(
                content='{"detail": "Invalid token"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            )
        
        # Adicionar dados do usuário ao request
        request.state.user = user_data
        
        return await call_next(request)


# Instância do security scheme para FastAPI
security = HTTPBearer()


def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Obter usuário atual do request (opcional)
    """
    return getattr(request.state, "user", None)


def get_current_user(request: Request) -> dict:
    """
    Obter usuário atual do request (obrigatório)
    """
    user = get_current_user_optional(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return user


def get_current_admin_user(request: Request) -> dict:
    """
    Obter usuário admin atual
    """
    user = get_current_user(request)
    
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user


def require_auth(func):
    """
    Decorator para exigir autenticação
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        
        # Tentar encontrar request nos argumentos
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            # Tentar encontrar nos kwargs
            request = kwargs.get("request")
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Request object not found"
            )
        
        user = get_current_user(request)
        
        # Adicionar user aos kwargs
        kwargs["current_user"] = user
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_admin(func):
    """
    Decorator para exigir admin
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        
        # Tentar encontrar request nos argumentos
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            request = kwargs.get("request")
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Request object not found"
            )
        
        user = get_current_admin_user(request)
        
        # Adicionar user aos kwargs
        kwargs["current_user"] = user
        
        return await func(*args, **kwargs)
    
    return wrapper
