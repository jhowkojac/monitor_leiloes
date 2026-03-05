from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    Modelo de usuário para autenticação JWT
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Campos para 2FA
    totp_secret = Column(String(32), nullable=True)  # Secret para TOTP
    backup_codes = Column(Text, nullable=True)  # JSON com códigos de backup
    is_2fa_enabled = Column(Boolean, default=False)  # Status do 2FA

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, active={self.is_active})>"

    def to_dict(self):
        """Convert user to dict (without sensitive data)"""
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "is_2fa_enabled": self.is_2fa_enabled
        }
