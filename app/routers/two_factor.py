"""Rotas para autenticação de dois fatores (2FA)."""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.two_factor import two_factor_service
from app.middleware.auth import get_current_user
import json

router = APIRouter(prefix="/api/2fa", tags=["2FA"])


class Setup2FARequest(BaseModel):
    """Request para configurar 2FA."""
    token: str


class Verify2FARequest(BaseModel):
    """Request para verificar 2FA."""
    token: str


class BackupCodeRequest(BaseModel):
    """Request para usar código de backup."""
    code: str


@router.post("/setup")
async def setup_2fa(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Inicia o setup de 2FA para o usuário atual.
    Retorna secret e QR code para configuração.
    """
    try:
        # Obter usuário atual
        user = get_current_user(request)
        db_user = db.query(User).filter(User.email == user["email"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se 2FA já está ativo
        if db_user.is_2fa_enabled:
            raise HTTPException(status_code=400, detail="2FA já está ativo")
        
        # Gerar secret e QR code
        secret = two_factor_service.generate_secret()
        qr_code = two_factor_service.generate_qr_code(db_user.email, secret)
        backup_codes = two_factor_service.generate_backup_codes()
        
        # Salvar secret e backup codes temporariamente (não ativar ainda)
        db_user.totp_secret = secret
        db_user.backup_codes = json.dumps(backup_codes)
        db.commit()
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "message": "Escaneie o QR code e use um código para ativar o 2FA"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao configurar 2FA: {str(e)}")


@router.post("/enable")
async def enable_2fa(
    request_data: Setup2FARequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Ativa 2FA após verificação do token.
    """
    try:
        # Obter usuário atual
        user = get_current_user(request)
        db_user = db.query(User).filter(User.email == user["email"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se tem secret configurado
        if not db_user.totp_secret:
            raise HTTPException(status_code=400, detail="2FA não foi configurado")
        
        # Verificar token
        if not two_factor_service.verify_token(db_user.totp_secret, request_data.token):
            raise HTTPException(status_code=400, detail="Token inválido")
        
        # Ativar 2FA
        db_user.is_2fa_enabled = True
        db.commit()
        
        return {
            "message": "2FA ativado com sucesso",
            "is_2fa_enabled": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ativar 2FA: {str(e)}")


@router.post("/disable")
async def disable_2fa(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Desativa 2FA para o usuário atual.
    """
    try:
        # Obter usuário atual
        user = get_current_user(request)
        db_user = db.query(User).filter(User.email == user["email"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Desativar 2FA
        db_user.is_2fa_enabled = False
        db_user.totp_secret = None
        db_user.backup_codes = None
        db.commit()
        
        return {
            "message": "2FA desativado com sucesso",
            "is_2fa_enabled": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao desativar 2FA: {str(e)}")


@router.get("/status")
async def get_2fa_status(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Retorna o status atual do 2FA do usuário.
    """
    try:
        # Obter usuário atual
        user = get_current_user(request)
        db_user = db.query(User).filter(User.email == user["email"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        backup_codes_count = 0
        if db_user.backup_codes:
            try:
                backup_codes = json.loads(db_user.backup_codes)
                backup_codes_count = len(backup_codes)
            except:
                backup_codes_count = 0
        
        return {
            "is_2fa_enabled": db_user.is_2fa_enabled,
            "has_backup_codes": bool(db_user.backup_codes),
            "backup_codes_count": backup_codes_count,
            "is_setup_pending": bool(db_user.totp_secret) and not db_user.is_2fa_enabled
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status 2FA: {str(e)}")


@router.post("/verify")
async def verify_2fa_token(
    request_data: Verify2FARequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verifica um token 2FA (usado no login).
    """
    try:
        # Obter usuário atual
        user = get_current_user(request)
        db_user = db.query(User).filter(User.email == user["email"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se 2FA está ativo
        if not db_user.is_2fa_enabled:
            raise HTTPException(status_code=400, detail="2FA não está ativo")
        
        # Verificar token
        if not two_factor_service.verify_token(db_user.totp_secret, request_data.token):
            raise HTTPException(status_code=400, detail="Token inválido")
        
        return {
            "valid": True,
            "message": "Token verificado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar token: {str(e)}")


@router.post("/backup-code")
async def use_backup_code(
    request_data: BackupCodeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Usa um código de backup para acesso.
    """
    try:
        # Obter usuário atual
        user = get_current_user(request)
        db_user = db.query(User).filter(User.email == user["email"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se tem códigos de backup
        if not db_user.backup_codes:
            raise HTTPException(status_code=400, detail="Não há códigos de backup disponíveis")
        
        # Parse dos códigos de backup
        try:
            backup_codes = json.loads(db_user.backup_codes)
        except:
            raise HTTPException(status_code=400, detail="Códigos de backup corrompidos")
        
        # Verificar código
        if not two_factor_service.verify_backup_code(backup_codes, request_data.code):
            raise HTTPException(status_code=400, detail="Código de backup inválido")
        
        # Atualizar códigos restantes
        db_user.backup_codes = json.dumps(backup_codes)
        db.commit()
        
        return {
            "valid": True,
            "message": "Código de backup verificado com sucesso",
            "remaining_codes": len(backup_codes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao usar código de backup: {str(e)}")


@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Gera novos códigos de backup.
    """
    try:
        # Obter usuário atual
        user = get_current_user(request)
        db_user = db.query(User).filter(User.email == user["email"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se 2FA está ativo
        if not db_user.is_2fa_enabled:
            raise HTTPException(status_code=400, detail="2FA não está ativo")
        
        # Gerar novos códigos
        new_backup_codes = two_factor_service.generate_backup_codes()
        db_user.backup_codes = json.dumps(new_backup_codes)
        db.commit()
        
        return {
            "backup_codes": new_backup_codes,
            "message": "Códigos de backup regenerados com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao regenerar códigos: {str(e)}")
