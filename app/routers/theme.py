"""
Theme Customization API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from app.services.theme import theme_service

logger = logging.getLogger(__name__)

router = APIRouter()

class ThemePreferences(BaseModel):
    theme: str
    customizations: Optional[Dict[str, Any]] = None
    auto_switch: bool = False
    system_preference: str = "default"  # light/dark/auto

class CustomThemeRequest(BaseModel):
    name: str
    base_theme: str = "default"
    customizations: Optional[Dict[str, Any]] = None

@router.get("/themes")
async def get_available_themes():
    """Retorna todos os temas disponíveis"""
    try:
        return {
            "themes": theme_service.get_all_themes(),
            "default_theme": theme_service.default_theme,
            "allow_custom": theme_service.allow_custom_themes
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter temas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter temas")

@router.get("/themes/{theme_name}")
async def get_theme_details(theme_name: str):
    """Retorna detalhes de um tema específico"""
    try:
        theme = theme_service.get_theme(theme_name)
        if not theme:
            raise HTTPException(status_code=404, detail="Tema não encontrado")
        
        return {
            "theme": theme,
            "css_variables": theme_service.get_css_variables(theme)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter tema: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter tema")

@router.get("/preferences/{user_id}")
async def get_user_theme_preferences(user_id: str):
    """Retorna preferências de tema do usuário"""
    try:
        return theme_service.get_user_preferences(user_id)
        
    except Exception as e:
        logger.error(f"Erro ao obter preferências: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter preferências")

@router.put("/preferences/{user_id}")
async def update_user_theme_preferences(
    user_id: str, 
    preferences: ThemePreferences
):
    """Atualiza preferências de tema do usuário"""
    try:
        # Validar tema
        theme = theme_service.get_theme(preferences.theme)
        if not theme and preferences.theme != "custom":
            raise HTTPException(status_code=400, detail="Tema inválido")
        
        # Salvar preferências
        success = theme_service.save_user_preferences(user_id, preferences.dict())
        
        return {
            "status": "updated" if success else "failed",
            "preferences": preferences.dict(),
            "theme": theme_service.get_theme(preferences.theme)
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar preferências: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar preferências")

@router.post("/custom")
async def create_custom_theme(theme_request: CustomThemeRequest):
    """Cria um tema customizado"""
    try:
        if not theme_service.allow_custom_themes:
            raise HTTPException(status_code=403, detail="Custom themes não permitidos")
        
        # Validar tema base
        base_theme = theme_service.get_theme(theme_request.base_theme)
        if not base_theme:
            raise HTTPException(status_code=400, detail="Tema base inválido")
        
        # Criar tema customizado
        custom_theme = theme_service.create_custom_theme(
            name=theme_request.name,
            base_theme=theme_request.base_theme,
            customizations=theme_request.customizations
        )
        
        return {
            "status": "created",
            "theme": custom_theme,
            "css_variables": theme_service.get_css_variables(custom_theme)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar tema customizado: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar tema")

@router.post("/validate")
async def validate_theme(theme_data: Dict[str, Any]):
    """Valida configuração de tema"""
    try:
        validation = theme_service.validate_theme(theme_data)
        return validation
        
    except Exception as e:
        logger.error(f"Erro ao validar tema: {e}")
        raise HTTPException(status_code=500, detail="Erro ao validar tema")

@router.get("/css/{theme_name}")
async def get_theme_css(theme_name: str):
    """Retorna CSS gerado para o tema"""
    try:
        theme = theme_service.get_theme(theme_name)
        if not theme:
            raise HTTPException(status_code=404, detail="Tema não encontrado")
        
        css_variables = theme_service.get_css_variables(theme)
        
        css_content = f"""
/* Theme: {theme.get('name', theme_name)} */
:root {{
{css_variables}
}}

/* Component styles with theme variables */
.card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--border-radius);
    box-shadow: var(--shadows-enabled) ? 0 4px 6px rgba(0, 0, 0, 0.1) : none;
}}

.header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
}}

body {{
    background: var(--background);
    color: var(--text);
    font-family: var(--font-primary);
}}

button {{
    background: var(--primary);
    color: var(--background);
    border-radius: var(--border-radius);
    font-family: var(--font-primary);
}}

code, .mono {{
    font-family: var(--font-mono);
}}
        """
        
        return {
            "theme_name": theme_name,
            "css_content": css_content,
            "css_variables": css_variables
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar CSS: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar CSS")

@router.delete("/custom/{theme_name}")
async def delete_custom_theme(theme_name: str):
    """Remove tema customizado"""
    try:
        if not theme_service.allow_custom_themes:
            raise HTTPException(status_code=403, detail="Custom themes não permitidos")
        
        # Aqui você removeria o tema do storage
        # Por ora, apenas log
        logger.info(f"Custom theme removido: {theme_name}")
        
        return {
            "status": "deleted",
            "theme_name": theme_name
        }
        
    except Exception as e:
        logger.error(f"Erro ao remover tema: {e}")
        raise HTTPException(status_code=500, detail="Erro ao remover tema")
