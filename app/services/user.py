from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional, Dict, Any


class UserService:
    """
    Serviço para gerenciamento de usuários
    """
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash da senha usando bcrypt"""
        # Truncar senha para evitar erro do bcrypt
        if len(password) > 72:
            password = password[:72]
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha contra hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, db: Session, email: str, password: str, is_admin: bool = False) -> User:
        """Criar novo usuário"""
        # Verificar se email já existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("Email já cadastrado")
        
        # Hash da senha (com truncação automática)
        password_hash = self.hash_password(password)
        
        # Criar usuário
        db_user = User(
            email=email,
            password_hash=password_hash,
            is_admin=is_admin
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Autenticar usuário por email e senha"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obter usuário por email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Obter usuário por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def update_user(self, db: Session, user_id: int, **kwargs) -> Optional[User]:
        """Atualizar dados do usuário"""
        user = self.get_user_by_id(db, user_id)
        
        if not user:
            return None
        
        # Atualizar campos permitidos
        allowed_fields = ["email", "is_active", "is_admin"]
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    def change_password(self, db: Session, user_id: int, new_password: str) -> bool:
        """Alterar senha do usuário"""
        user = self.get_user_by_id(db, user_id)
        
        if not user:
            return False
        
        user.password_hash = self.hash_password(new_password)
        db.commit()
        
        return True
    
    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Desativar usuário"""
        user = self.get_user_by_id(db, user_id)
        
        if not user:
            return False
        
        user.is_active = False
        db.commit()
        
        return True


# Instância global do serviço
user_service = UserService()
