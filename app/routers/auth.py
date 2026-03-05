from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user import user_service
from app.services.jwt import jwt_service
from app.middleware.auth import get_current_user, get_current_user_optional
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()


# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool
    created_at: str


@router.post("/login")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login
    """
    try:
        # Autenticar usuário
        user = user_service.authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Verificar se 2FA está ativo
        if user.is_2fa_enabled:
            # Retornar resposta indicando que 2FA é necessário
            return {
                "requires_2fa": True,
                "message": "Autenticação de dois fatores necessária",
                "user_id": user.id,
                "temp_token": jwt_service.create_temp_token(user.id)  # Token temporário para 2FA
            }
        
        # Criar tokens (sem 2FA)
        tokens = jwt_service.create_tokens_for_user(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin
        )
        
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user.to_dict()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/login-2fa")
async def login_with_2fa(
    login_data: LoginRequest,
    two_fa_code: str,
    temp_token: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login com verificação 2FA
    """
    try:
        # Verificar token temporário
        temp_payload = jwt_service.verify_temp_token(temp_token)
        if not temp_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token temporário inválido ou expirado"
            )
        
        user_id = int(temp_payload.get("sub"))
        
        # Obter usuário
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar se 2FA está ativo
        if not user.is_2fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA não está ativo para este usuário"
            )
        
        # Verificar token 2FA
        from app.services.two_factor import two_factor_service
        if not two_factor_service.verify_token(user.totp_secret, two_fa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código 2FA inválido"
            )
        
        # Criar tokens definitivos
        tokens = jwt_service.create_tokens_for_user(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin
        )
        
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no login 2FA: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshRequest
):
    """
    Endpoint para refresh token
    """
    try:
        # Gerar novo access token
        new_access_token = jwt_service.refresh_access_token(refresh_data.refresh_token)
        
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado"
            )
        
        return RefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=30 * 60  # 30 minutos em segundos
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/logout")
async def logout(
    request: Request
):
    """
    Endpoint de logout (client-side only)
    """
    # Em uma implementação real, poderíamos adicionar o token a uma blacklist
    # Por enquanto, o logout é feito client-side removendo o token
    return {"message": "Logout realizado com sucesso"}


@router.get("/me")
async def get_current_user_info(
    request: Request
):
    """
    Obter informações do usuário atual
    """
    user = get_current_user(request)
    
    # Obter dados completos do usuário do banco
    db = next(get_db())
    db_user = user_service.get_user_by_id(db, user["user_id"])
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        is_active=db_user.is_active,
        is_admin=db_user.is_admin,
        created_at=db_user.created_at.isoformat() if db_user.created_at else ""
    )


@router.get("/verify")
async def verify_token(
    request: Request
):
    """
    Verificar se o token é válido
    """
    user = get_current_user_optional(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    return {
        "valid": True,
        "user": {
            "id": user["user_id"],
            "email": user["email"],
            "is_admin": user["is_admin"]
        }
    }
