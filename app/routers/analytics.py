"""
Advanced Analytics API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import time

from app.services.analytics import analytics_service, AnalyticsEvent

logger = logging.getLogger(__name__)

router = APIRouter()

class AnalyticsEventRequest(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Optional[Dict] = None

class PerformanceMetric(BaseModel):
    metric_name: str
    value: float
    unit: str = "ms"

@router.post("/track")
async def track_analytics_event(event: AnalyticsEventRequest):
    """Registra evento de analytics"""
    try:
        analytics_event = AnalyticsEvent(
            event_type=event.event_type,
            user_id=event.user_id,
            session_id=event.session_id,
            data=event.data
        )
        
        analytics_service.track_event(analytics_event)
        
        return {
            "status": "tracked",
            "event_type": event.event_type,
            "timestamp": analytics_event.timestamp
        }
        
    except Exception as e:
        logger.error(f"Erro ao track evento: {e}")
        raise HTTPException(status_code=500, detail="Erro ao track evento")

@router.post("/performance")
async def track_performance_metric(metric: PerformanceMetric):
    """Registra métrica de performance"""
    try:
        analytics_service.track_performance(
            metric_name=metric.metric_name,
            value=metric.value,
            unit=metric.unit
        )
        
        return {
            "status": "tracked",
            "metric": metric.metric_name,
            "value": metric.value,
            "unit": metric.unit
        }
        
    except Exception as e:
        logger.error(f"Erro ao track métrica: {e}")
        raise HTTPException(status_code=500, detail="Erro ao track métrica")

@router.get("/dashboard")
async def get_analytics_dashboard():
    """Retorna dashboard completo de analytics"""
    try:
        return {
            "real_time": analytics_service.get_real_time_stats(minutes=5),
            "user_analytics": analytics_service.get_user_analytics(days=7),
            "page_analytics": analytics_service.get_page_analytics(days=7),
            "performance": analytics_service.get_performance_analytics(hours=24),
            "funnel": analytics_service.get_funnel_analytics(days=7),
            "summary": {
                "total_events": len(analytics_service.events),
                "active_sessions": len(analytics_service.sessions),
                "unique_users": len(analytics_service.user_profiles),
                "timestamp": time.time()
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter dashboard")

@router.get("/users/{user_id}")
async def get_user_analytics(user_id: str, days: int = Query(30, ge=1, le=365)):
    """Retorna analytics detalhadas de usuário"""
    try:
        return analytics_service.get_user_analytics(user_id=user_id, days=days)
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics do usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter analytics do usuário")

@router.get("/pages")
async def get_page_analytics(
    page: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365)
):
    """Retorna analytics de páginas"""
    try:
        return analytics_service.get_page_analytics(page=page, days=days)
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics de páginas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter analytics de páginas")

@router.get("/performance")
async def get_performance_analytics(hours: int = Query(24, ge=1, le=168)):
    """Retorna analytics de performance"""
    try:
        return analytics_service.get_performance_analytics(hours=hours)
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics de performance: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter analytics de performance")

@router.get("/funnel")
async def get_funnel_analytics(days: int = Query(30, ge=1, le=365)):
    """Retorna análise de funil"""
    try:
        return analytics_service.get_funnel_analytics(days=days)
        
    except Exception as e:
        logger.error(f"Erro ao obter análise de funil: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter análise de funil")

@router.get("/real-time")
async def get_real_time_analytics(minutes: int = Query(5, ge=1, le=60)):
    """Retorna estatísticas em tempo real"""
    try:
        return analytics_service.get_real_time_stats(minutes=minutes)
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics em tempo real: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter analytics em tempo real")

@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", regex="^(json|csv)$"),
    days: int = Query(30, ge=1, le=365)
):
    """Exporta dados de analytics"""
    try:
        return analytics_service.export_analytics(format=format, days=days)
        
    except Exception as e:
        logger.error(f"Erro ao exportar analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro ao exportar analytics")

@router.get("/events")
async def get_events_list(
    event_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Retorna lista de eventos com filtros"""
    try:
        # Filtrar eventos
        filtered_events = []
        for event in analytics_service.events:
            if event_type and event.event_type != event_type:
                continue
            if user_id and event.user_id != user_id:
                continue
            filtered_events.append(event)
        
        # Paginar
        total_events = len(filtered_events)
        paginated_events = filtered_events[offset:offset + limit]
        
        return {
            "total_events": total_events,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_events,
            "events": [
                {
                    "timestamp": e.timestamp,
                    "datetime": e.datetime.isoformat(),
                    "event_type": e.event_type,
                    "user_id": e.user_id,
                    "session_id": e.session_id,
                    "data": e.data
                }
                for e in paginated_events
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar eventos")

@router.delete("/reset")
async def reset_analytics_data():
    """Reseta dados de analytics (admin only)"""
    try:
        # Limpar dados
        analytics_service.events.clear()
        analytics_service.sessions.clear()
        analytics_service.user_profiles.clear()
        analytics_service.page_views.clear()
        analytics_service.events_count.clear()
        analytics_service.performance_metrics.clear()
        
        logger.info("Analytics data resetado")
        
        return {
            "status": "reset",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Erro ao resetar analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro ao resetar analytics")
