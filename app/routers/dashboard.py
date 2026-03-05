"""Rotas do Dashboard Administrativo."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.dashboard import dashboard_service
from app.middleware.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


class UserUpdateRequest(BaseModel):
    """Request para atualizar usuário."""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_2fa_enabled: Optional[bool] = None


class UserSearchRequest(BaseModel):
    """Request para busca de usuários."""
    query: str
    limit: int = 20


def require_admin(current_user: dict = Depends(get_current_user)):
    """Middleware para exigir permissões de admin."""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=403,
            detail="Permissões de administrador necessárias"
        )
    return current_user


@router.get("/overview")
async def get_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retorna estatísticas gerais do sistema.
    """
    try:
        stats = dashboard_service.get_overview_stats(db)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )


@router.get("/user-growth")
async def get_user_growth(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retorna dados de crescimento de usuários.
    """
    try:
        growth_data = dashboard_service.get_user_growth_data(db, days)
        return {
            "success": True,
            "data": growth_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar dados de crescimento: {str(e)}"
        )


@router.get("/2fa-stats")
async def get_2fa_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retorna estatísticas de 2FA.
    """
    try:
        stats = dashboard_service.get_2fa_stats(db)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas 2FA: {str(e)}"
        )


@router.get("/recent-users")
async def get_recent_users(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retorna usuários mais recentes.
    """
    try:
        users = dashboard_service.get_recent_users(db, limit)
        return {
            "success": True,
            "data": users
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar usuários recentes: {str(e)}"
        )


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retorna detalhes de um usuário específico.
    """
    try:
        user_details = dashboard_service.get_user_details(db, user_id)
        
        if not user_details:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado"
            )
        
        return {
            "success": True,
            "data": user_details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar detalhes do usuário: {str(e)}"
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    updates: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Atualiza dados de um usuário.
    """
    try:
        # Impedir que um admin desative a si mesmo
        if user_id == current_user["id"] and updates.is_active is False:
            raise HTTPException(
                status_code=400,
                detail="Você não pode desativar seu próprio usuário"
            )
        
        # Impedir que um admin remova seu próprio status de admin
        if user_id == current_user["id"] and updates.is_admin is False:
            raise HTTPException(
                status_code=400,
                detail="Você não pode remover seu próprio status de administrador"
            )
        
        success = dashboard_service.update_user_status(db, user_id, updates.dict(exclude_unset=True))
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado"
            )
        
        return {
            "success": True,
            "message": "Usuário atualizado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )


@router.get("/system-health")
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retorna status de saúde do sistema.
    """
    try:
        health = dashboard_service.get_system_health(db)
        return {
            "success": True,
            "data": health
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar saúde do sistema: {str(e)}"
        )


@router.post("/search-users")
async def search_users(
    search_request: UserSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Busca usuários por email.
    """
    try:
        users = dashboard_service.search_users(db, search_request.query, search_request.limit)
        return {
            "success": True,
            "data": users
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca de usuários: {str(e)}"
        )


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Retorna todas as estatísticas do dashboard em uma única chamada.
    """
    try:
        # Buscar todas as estatísticas
        overview = dashboard_service.get_overview_stats(db)
        two_fa_stats = dashboard_service.get_2fa_stats(db)
        recent_users = dashboard_service.get_recent_users(db, 5)
        system_health = dashboard_service.get_system_health(db)
        user_growth = dashboard_service.get_user_growth_data(db, 7)
        
        return {
            "success": True,
            "data": {
                "overview": overview,
                "two_fa_stats": two_fa_stats,
                "recent_users": recent_users,
                "system_health": system_health,
                "user_growth": user_growth
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas do dashboard: {str(e)}"
        )
