from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import settings


class JWTService:
    """
    Serviço para gerenciamento de tokens JWT
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Criar token de acesso"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Criar token de refresh"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verificar e decodificar token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar tipo do token
            if payload.get("type") != token_type:
                return None
            
            # Verificar expiração (já feito pelo jwt.decode)
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            return payload
        
        except JWTError:
            return None
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Obter dados do usuário a partir do token"""
        payload = self.verify_token(token, "access")
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        email = payload.get("email")
        is_admin = payload.get("is_admin", False)
        
        if not user_id or not email:
            return None
        
        return {
            "user_id": int(user_id),
            "email": email,
            "is_admin": is_admin
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Gerar novo access token usando refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        email = payload.get("email")
        is_admin = payload.get("is_admin", False)
        
        if not user_id or not email:
            return None
        
        # Criar novo access token
        new_token_data = {
            "sub": str(user_id),
            "email": email,
            "is_admin": is_admin
        }
        
        return self.create_access_token(new_token_data)
    
    def create_temp_token(self, user_id: int) -> str:
        """Cria um token temporário para verificação 2FA (5 minutos)."""
        expires_delta = timedelta(minutes=5)
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": str(user_id),
            "type": "2fa_temp",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_temp_token(self, token: str) -> Optional[dict]:
        """Verifica um token temporário 2FA."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar se é um token temporário 2FA
            if payload.get("type") != "2fa_temp":
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def create_tokens_for_user(self, user_id: int, email: str, is_admin: bool = False) -> Dict[str, str]:
        """Criar par de tokens (access + refresh) para usuário"""
        token_data = {
            "sub": str(user_id),
            "email": email,
            "is_admin": is_admin
        }
        
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60  # em segundos
        }


# Instância global do serviço
jwt_service = JWTService()
