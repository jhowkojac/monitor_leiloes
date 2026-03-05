"""
Theme Customization Service
"""
import json
import os
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ThemeService:
    """Serviço de customização de temas"""
    
    def __init__(self):
        self.themes = {
            "default": {
                "name": "Padrão",
                "colors": {
                    "primary": "#c9a227",
                    "secondary": "#a68520",
                    "accent": "#2d7d46",
                    "background": "#0f0f12",
                    "surface": "#18181c",
                    "text": "#e8e6e3",
                    "muted": "#8b8685",
                    "border": "#2a2a32"
                },
                "fonts": {
                    "primary": "'Outfit', sans-serif",
                    "mono": "'JetBrains Mono', monospace"
                },
                "border_radius": "10px",
                "shadows": "enabled"
            },
            "dark": {
                "name": "Escuro",
                "colors": {
                    "primary": "#c9a227",
                    "secondary": "#a68520", 
                    "accent": "#2d7d46",
                    "background": "#0a0a0f",
                    "surface": "#141418",
                    "text": "#e1e1e6",
                    "muted": "#9ca3af",
                    "border": "#2a2a32"
                },
                "fonts": {
                    "primary": "'Outfit', sans-serif",
                    "mono": "'JetBrains Mono', monospace"
                },
                "border_radius": "10px",
                "shadows": "enabled"
            },
            "light": {
                "name": "Claro",
                "colors": {
                    "primary": "#c9a227",
                    "secondary": "#a68520",
                    "accent": "#2d7d46",
                    "background": "#ffffff",
                    "surface": "#f8f9fa",
                    "text": "#212529",
                    "muted": "#6c757d",
                    "border": "#dee2e6"
                },
                "fonts": {
                    "primary": "'Outfit', sans-serif",
                    "mono": "'JetBrains Mono', monospace"
                },
                "border_radius": "8px",
                "shadows": "subtle"
            },
            "high_contrast": {
                "name": "Alto Contraste",
                "colors": {
                    "primary": "#ff6b35",
                    "secondary": "#ff8c42",
                    "accent": "#28a745",
                    "background": "#000000",
                    "surface": "#1a1a1a",
                    "text": "#ffffff",
                    "muted": "#cccccc",
                    "border": "#404040"
                },
                "fonts": {
                    "primary": "'Outfit', sans-serif",
                    "mono": "'JetBrains Mono', monospace"
                },
                "border_radius": "0px",
                "shadows": "disabled"
            }
        }
        
        # Configurações padrão
        self.default_theme = os.getenv("DEFAULT_THEME", "default")
        self.allow_custom_themes = os.getenv("ALLOW_CUSTOM_THEMES", "true").lower() == "true"
        
    def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Obtém configuração do tema"""
        return self.themes.get(theme_name)
    
    def get_all_themes(self) -> Dict[str, Dict[str, Any]]:
        """Retorna todos os temas disponíveis"""
        return self.themes
    
    def validate_theme(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida configuração de tema"""
        errors = []
        
        # Validar cores
        if "colors" in theme_data:
            required_colors = ["primary", "background", "text"]
            for color in required_colors:
                if color not in theme_data["colors"]:
                    errors.append(f"Cor '{color}' é obrigatória")
        
        # Validar fontes
        if "fonts" in theme_data:
            required_fonts = ["primary"]
            for font in required_fonts:
                if font not in theme_data["fonts"]:
                    errors.append(f"Fonte '{font}' é obrigatória")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def create_custom_theme(self, name: str, base_theme: str = "default", 
                        customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cria tema customizado baseado em outro tema"""
        if not self.allow_custom_themes:
            raise ValueError("Custom themes não permitidos")
        
        base = self.themes.get(base_theme, self.themes["default"])
        custom_theme = {
            "name": name,
            "base_theme": base_theme,
            "custom": True
        }
        
        # Aplicar customizações
        if customizations:
            if "colors" in customizations:
                theme_colors = base["colors"].copy()
                theme_colors.update(customizations["colors"])
                custom_theme["colors"] = theme_colors
            
            if "fonts" in customizations:
                theme_fonts = base["fonts"].copy()
                theme_fonts.update(customizations["fonts"])
                custom_theme["fonts"] = theme_fonts
            
            if "border_radius" in customizations:
                custom_theme["border_radius"] = customizations["border_radius"]
            
            if "shadows" in customizations:
                custom_theme["shadows"] = customizations["shadows"]
        
        return custom_theme
    
    def get_css_variables(self, theme_data: Dict[str, Any]) -> str:
        """Gera variáveis CSS para o tema"""
        colors = theme_data.get("colors", {})
        fonts = theme_data.get("fonts", {})
        border_radius = theme_data.get("border_radius", "10px")
        
        css_vars = []
        for key, value in colors.items():
            css_vars.append(f"--{key}: {value};")
        
        for key, value in fonts.items():
            css_vars.append(f"--font-{key}: {value};")
        
        css_vars.append(f"--border-radius: {border_radius};")
        
        return "\n".join(css_vars)
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Obtém preferências do usuário (em produção usar Redis/Database)"""
        # Por ora, retornar preferências padrão
        return {
            "theme": self.default_theme,
            "customizations": {},
            "auto_switch": False,
            "system_preference": "default"  # light/dark/auto
        }
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Salva preferências do usuário (em produção usar Redis/Database)"""
        # Por ora, apenas log
        logger.info(f"Preferências salvas para usuário {user_id}: {preferences}")
        return True

# Instância global
theme_service = ThemeService()
