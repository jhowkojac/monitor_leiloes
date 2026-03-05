"""Serviço de Dashboard Administrativo."""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.user import User
import json


class DashboardService:
    """Serviço para gerenciamento do dashboard administrativo."""
    
    def __init__(self):
        pass
    
    def get_overview_stats(self, db: Session) -> Dict[str, Any]:
        """Estatísticas gerais do sistema."""
        try:
            # Total de usuários
            total_users = db.query(User).count()
            
            # Usuários ativos
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Usuários com 2FA
            users_with_2fa = db.query(User).filter(User.is_2fa_enabled == True).count()
            
            # Usuários admin
            admin_users = db.query(User).filter(User.is_admin == True).count()
            
            # Usuários criados nos últimos 7 dias
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            new_users = db.query(User).filter(User.created_at >= seven_days_ago).count()
            
            # Taxa de adoção 2FA
            two_fa_adoption_rate = (users_with_2fa / total_users * 100) if total_users > 0 else 0
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "users_with_2fa": users_with_2fa,
                "admin_users": admin_users,
                "new_users_last_7_days": new_users,
                "two_fa_adoption_rate": round(two_fa_adoption_rate, 2),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return {}
    
    def get_user_growth_data(self, db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Dados de crescimento de usuários."""
        try:
            # Buscar usuários criados nos últimos X dias
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query para agrupar por dia
            result = db.query(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            ).filter(
                User.created_at >= start_date
            ).group_by(
                func.date(User.created_at)
            ).order_by('date').all()
            
            # Formatar dados
            growth_data = []
            for date, count in result:
                growth_data.append({
                    "date": date.isoformat(),
                    "new_users": count
                })
            
            return growth_data
            
        except Exception as e:
            print(f"Erro ao buscar dados de crescimento: {e}")
            return []
    
    def get_2fa_stats(self, db: Session) -> Dict[str, Any]:
        """Estatísticas de 2FA."""
        try:
            total_users = db.query(User).count()
            
            if total_users == 0:
                return {
                    "total_users": 0,
                    "enabled_2fa": 0,
                    "disabled_2fa": 0,
                    "adoption_rate": 0
                }
            
            enabled_2fa = db.query(User).filter(User.is_2fa_enabled == True).count()
            disabled_2fa = total_users - enabled_2fa
            adoption_rate = (enabled_2fa / total_users * 100)
            
            return {
                "total_users": total_users,
                "enabled_2fa": enabled_2fa,
                "disabled_2fa": disabled_2fa,
                "adoption_rate": round(adoption_rate, 2)
            }
            
        except Exception as e:
            print(f"Erro ao buscar estatísticas 2FA: {e}")
            return {}
    
    def get_recent_users(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Usuários mais recentes."""
        try:
            users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
            
            recent_users = []
            for user in users:
                recent_users.append({
                    "id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_admin": user.is_admin,
                    "is_2fa_enabled": user.is_2fa_enabled,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                })
            
            return recent_users
            
        except Exception as e:
            print(f"Erro ao buscar usuários recentes: {e}")
            return []
    
    def get_user_details(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """Detalhes de um usuário específico."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None
            
            # Verificar se tem códigos de backup
            backup_codes_count = 0
            if user.backup_codes:
                try:
                    backup_codes = json.loads(user.backup_codes)
                    backup_codes_count = len(backup_codes)
                except:
                    backup_codes_count = 0
            
            return {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "is_2fa_enabled": user.is_2fa_enabled,
                "has_backup_codes": bool(user.backup_codes),
                "backup_codes_count": backup_codes_count,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
        except Exception as e:
            print(f"Erro ao buscar detalhes do usuário: {e}")
            return None
    
    def update_user_status(self, db: Session, user_id: int, updates: Dict[str, Any]) -> bool:
        """Atualiza status de um usuário."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            # Atualizar campos permitidos
            if 'is_active' in updates:
                user.is_active = updates['is_active']
            
            if 'is_admin' in updates:
                user.is_admin = updates['is_admin']
            
            # Para 2FA, precisamos cuidado especial
            if 'is_2fa_enabled' in updates and not updates['is_2fa_enabled']:
                # Desativar 2FA - limpar secrets
                user.is_2fa_enabled = False
                user.totp_secret = None
                user.backup_codes = None
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Erro ao atualizar usuário: {e}")
            return False
    
    def get_system_health(self, db: Session) -> Dict[str, Any]:
        """Verificação de saúde do sistema."""
        try:
            # Estatísticas do banco
            user_count = db.query(User).count()
            
            # Verificar se há usuários admin
            admin_count = db.query(User).filter(User.is_admin == True).count()
            
            # Verificar se há usuários ativos
            active_count = db.query(User).filter(User.is_active == True).count()
            
            # Status do sistema
            health_status = "healthy"
            issues = []
            
            if admin_count == 0:
                health_status = "warning"
                issues.append("Nenhum usuário admin encontrado")
            
            if active_count == 0:
                health_status = "critical"
                issues.append("Nenhum usuário ativo encontrado")
            
            return {
                "status": health_status,
                "issues": issues,
                "database_connected": True,
                "user_count": user_count,
                "admin_count": admin_count,
                "active_count": active_count,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "issues": [f"Erro na verificação: {str(e)}"],
                "database_connected": False,
                "last_check": datetime.utcnow().isoformat()
            }
    
    def search_users(self, db: Session, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca usuários por email."""
        try:
            users = db.query(User).filter(
                User.email.ilike(f"%{query}%")
            ).limit(limit).all()
            
            search_results = []
            for user in users:
                search_results.append({
                    "id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_admin": user.is_admin,
                    "is_2fa_enabled": user.is_2fa_enabled,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
            
            return search_results
            
        except Exception as e:
            print(f"Erro na busca de usuários: {e}")
            return []


# Instância global do serviço
dashboard_service = DashboardService()
