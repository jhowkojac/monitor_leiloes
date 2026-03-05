"""Serviço de autenticação de dois fatores (2FA)."""
import pyotp
import qrcode
import io
import base64
from typing import Optional, Tuple, List
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session


class TwoFactorAuthService:
    """Serviço para gerenciamento de 2FA."""
    
    def __init__(self):
        self.app_name = "Monitor de Leilões"
        self.issuer_name = "Monitor Leilões"
    
    def generate_secret(self) -> str:
        """Gera um novo secret para 2FA."""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """Gera QR code para Google Authenticator."""
        # Criar URI TOTP
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        # Gerar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Converter para imagem base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Codificar em base64
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{qr_base64}"
    
    def verify_token(self, secret: str, token: str) -> bool:
        """Verifica se o token 2FA é válido."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Permite 1 step de tolerância
    
    def generate_backup_codes(self) -> List[str]:
        """Gera códigos de backup (10 códigos de 8 dígitos)."""
        import random
        import string
        
        codes = []
        for _ in range(10):
            code = ''.join(random.choices(string.digits, k=8))
            codes.append(code)
        
        return codes
    
    def verify_backup_code(self, user_backup_codes: List[str], provided_code: str) -> bool:
        """Verifica se o código de backup é válido e o remove da lista."""
        if provided_code in user_backup_codes:
            user_backup_codes.remove(provided_code)
            return True
        return False
    
    def enable_2fa_for_user(self, db: Session, user_id: int, secret: str, backup_codes: List[str]) -> bool:
        """Ativa 2FA para um usuário."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Adicionar colunas 2FA ao modelo (se não existirem)
            if not hasattr(user, 'totp_secret'):
                # Precisamos adicionar as colunas ao banco
                return False
            
            user.totp_secret = secret
            user.backup_codes = backup_codes
            user.is_2fa_enabled = True
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao habilitar 2FA: {e}")
            return False
    
    def disable_2fa_for_user(self, db: Session, user_id: int) -> bool:
        """Desativa 2FA para um usuário."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.totp_secret = None
            user.backup_codes = None
            user.is_2fa_enabled = False
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao desabilitar 2FA: {e}")
            return False
    
    def get_user_2fa_status(self, db: Session, user_id: int) -> Optional[dict]:
        """Retorna o status 2FA do usuário."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            return {
                'is_enabled': getattr(user, 'is_2fa_enabled', False),
                'has_backup_codes': bool(getattr(user, 'backup_codes', None)),
                'backup_codes_count': len(getattr(user, 'backup_codes', [])) if getattr(user, 'backup_codes', None) else 0
            }
            
        except Exception as e:
            print(f"Erro ao verificar status 2FA: {e}")
            return None


# Instância global do serviço
two_factor_service = TwoFactorAuthService()
