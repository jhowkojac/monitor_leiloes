"""
reCAPTCHA v3 Configuration Endpoint
"""
from fastapi import APIRouter, HTTPException
from app.services.recaptcha import recaptcha_config, get_recaptcha_html
import os

router = APIRouter()

@router.get("/recaptcha/config")
async def get_recaptcha_config():
    """Retorna configuração do reCAPTCHA para o frontend"""
    return recaptcha_config.get_frontend_config()

@router.get("/recaptcha/status")
async def get_recaptcha_status():
    """Retorna status do reCAPTCHA"""
    validation = recaptcha_config.validate_config()
    return {
        "configured": recaptcha_config.is_configured(),
        "enabled": recaptcha_config.enabled,
        "validation": validation
    }

@router.get("/recaptcha/html")
async def get_recaptcha_html_endpoint():
    """Retorna HTML do reCAPTCHA para inclusão em templates"""
    return {"html": get_recaptcha_html()}
