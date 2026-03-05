"""
reCAPTCHA v3 Configuration and Utilities
"""
import os
from typing import Dict, Any
import json

class RecaptchaConfig:
    """Configuração do reCAPTCHA v3"""
    
    def __init__(self):
        self.site_key = os.getenv("RECAPTCHA_SITE_KEY", "")
        self.secret_key = os.getenv("RECAPTCHA_SECRET_KEY", "")
        self.min_score = float(os.getenv("RECAPTCHA_MIN_SCORE", "0.5"))
        self.enabled = os.getenv("RECAPTCHA_ENABLED", "true").lower() == "true"
        
    def is_configured(self) -> bool:
        """Verifica se o reCAPTCHA está configurado"""
        return bool(self.site_key and self.secret_key)
    
    def get_frontend_config(self) -> Dict[str, Any]:
        """Retorna configuração para o frontend"""
        return {
            "siteKey": self.site_key,
            "enabled": self.enabled and self.is_configured(),
            "minScore": self.min_score
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Valida a configuração"""
        issues = []
        
        if not self.site_key:
            issues.append("RECAPTCHA_SITE_KEY não configurado")
        
        if not self.secret_key:
            issues.append("RECAPTCHA_SECRET_KEY não configurado")
        
        if self.min_score < 0.0 or self.min_score > 1.0:
            issues.append("RECAPTCHA_MIN_SCORE deve estar entre 0.0 e 1.0")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

# Instância global
recaptcha_config = RecaptchaConfig()

# Configuração para desenvolvimento
DEV_CONFIG = {
    "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEbQjVQ0MkQ9qM",  # Google test key
    "secret_key": "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe",  # Google test secret
    "min_score": 0.5
}

def get_recaptcha_script() -> str:
    """Retorna o script do reCAPTCHA v3"""
    if recaptcha_config.is_configured():
        return f"https://www.google.com/recaptcha/api.js?render={recaptcha_config.site_key}"
    return ""

def get_recaptcha_html() -> str:
    """Retorna o HTML do reCAPTCHA para templates"""
    if recaptcha_config.enabled and recaptcha_config.is_configured():
        return f"""
        <script src="{get_recaptcha_script()}" async defer></script>
        <script>
        window.recaptchaConfig = {json.dumps(recaptcha_config.get_frontend_config())};
        </script>
        """
    return "<!-- reCAPTCHA desabilitado ou não configurado -->"
