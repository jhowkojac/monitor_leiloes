"""
Advanced Analytics Service
"""
import time
import json
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AnalyticsEvent:
    """Evento de analytics"""
    
    def __init__(self, event_type: str, user_id: Optional[str] = None, 
                 session_id: Optional[str] = None, data: Optional[Dict] = None):
        self.event_type = event_type
        self.user_id = user_id
        self.session_id = session_id
        self.data = data or {}
        self.timestamp = time.time()
        self.datetime = datetime.fromtimestamp(self.timestamp)

class AnalyticsService:
    """Serviço de analytics avançado"""
    
    def __init__(self):
        self.events = deque(maxlen=10000)  # Últimos 10k eventos
        self.sessions = defaultdict(dict)
        self.user_profiles = defaultdict(dict)
        self.page_views = defaultdict(int)
        self.events_count = defaultdict(int)
        self.performance_metrics = deque(maxlen=1000)
        
    def track_event(self, event: AnalyticsEvent):
        """Registra evento de analytics"""
        self.events.append(event)
        self.events_count[event.event_type] += 1
        
        # Atualizar perfil do usuário
        if event.user_id:
            self._update_user_profile(event.user_id, event)
        
        # Atualizar sessão
        if event.session_id:
            self._update_session(event.session_id, event)
        
        logger.info(f"Analytics event: {event.event_type} - User: {event.user_id}")
    
    def _update_user_profile(self, user_id: str, event: AnalyticsEvent):
        """Atualiza perfil do usuário"""
        profile = self.user_profiles[user_id]
        
        # Atualizar dados básicos
        profile["first_seen"] = min(
            profile.get("first_seen", event.timestamp),
            event.timestamp
        )
        profile["last_seen"] = max(
            profile.get("last_seen", event.timestamp),
            event.timestamp
        )
        profile["total_events"] = profile.get("total_events", 0) + 1
        
        # Atualizar dados específicos por tipo
        if event.event_type == "page_view":
            profile["page_views"] = profile.get("page_views", 0) + 1
            profile["last_page"] = event.data.get("page", "")
        elif event.event_type == "login":
            profile["login_count"] = profile.get("login_count", 0) + 1
            profile["last_login"] = event.timestamp
        elif event.event_type == "search":
            profile["searches"] = profile.get("searches", 0) + 1
        elif event.event_type == "filter":
            profile["filters"] = profile.get("filters", 0) + 1
    
    def _update_session(self, session_id: str, event: AnalyticsEvent):
        """Atualiza dados da sessão"""
        session = self.sessions[session_id]
        
        session["start_time"] = min(
            session.get("start_time", event.timestamp),
            event.timestamp
        )
        session["last_activity"] = max(
            session.get("last_activity", event.timestamp),
            event.timestamp
        )
        session["duration"] = session["last_activity"] - session["start_time"]
        session["event_count"] = session.get("event_count", 0) + 1
        session["user_id"] = event.user_id
        session["pages"] = session.get("pages", [])
        
        if event.event_type == "page_view":
            page = event.data.get("page", "")
            if page not in session["pages"]:
                session["pages"].append(page)
    
    def track_performance(self, metric_name: str, value: float, unit: str = "ms"):
        """Registra métrica de performance"""
        self.performance_metrics.append({
            "name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": time.time()
        })
    
    def get_user_analytics(self, user_id: str, days: int = 30) -> Dict:
        """Retorna analytics de usuário específico"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        user_events = [
            event for event in self.events
            if event.user_id == user_id and event.timestamp >= cutoff_time
        ]
        
        if not user_events:
            return {"user_id": user_id, "message": "No data found"}
        
        # Análise de comportamento
        page_views = [e for e in user_events if e.event_type == "page_view"]
        searches = [e for e in user_events if e.event_type == "search"]
        logins = [e for e in user_events if e.event_type == "login"]
        
        # Páginas mais visitadas
        page_counts = defaultdict(int)
        for pv in page_views:
            page = pv.data.get("page", "unknown")
            page_counts[page] += 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_events": len(user_events),
            "page_views": len(page_views),
            "searches": len(searches),
            "logins": len(logins),
            "top_pages": sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "first_seen": datetime.fromtimestamp(min(e.timestamp for e in user_events)),
            "last_seen": datetime.fromtimestamp(max(e.timestamp for e in user_events)),
            "avg_session_duration": self._calculate_avg_session_duration(user_id)
        }
    
    def get_page_analytics(self, page: str = None, days: int = 30) -> Dict:
        """Retorna analytics de páginas"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        page_events = [
            event for event in self.events
            if event.event_type == "page_view" and event.timestamp >= cutoff_time
        ]
        
        if page:
            page_events = [e for e in page_events if e.data.get("page") == page]
        
        if not page_events:
            return {"message": "No data found"}
        
        # Análise de páginas
        page_counts = defaultdict(int)
        unique_users = set()
        total_time = 0
        
        for pv in page_events:
            page_name = pv.data.get("page", "unknown")
            page_counts[page_name] += 1
            if pv.user_id:
                unique_users.add(pv.user_id)
            total_time += pv.data.get("load_time", 0)
        
        return {
            "period_days": days,
            "total_page_views": len(page_events),
            "unique_pages": len(page_counts),
            "unique_users": len(unique_users),
            "top_pages": sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:20],
            "avg_load_time": total_time / len(page_events) if page_events else 0,
            "page_filter": page
        }
    
    def get_performance_analytics(self, hours: int = 24) -> Dict:
        """Retorna analytics de performance"""
        cutoff_time = time.time() - (hours * 60 * 60)
        
        recent_metrics = [
            metric for metric in self.performance_metrics
            if metric["timestamp"] >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": "No performance data"}
        
        # Agrupar por tipo de métrica
        metrics_by_name = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_name[metric["name"]].append(metric["value"])
        
        # Calcular estatísticas
        performance_stats = {}
        for name, values in metrics_by_name.items():
            performance_stats[name] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 0 else 0,
                "unit": recent_metrics[0]["unit"] if recent_metrics else "ms"
            }
        
        return {
            "period_hours": hours,
            "total_metrics": len(recent_metrics),
            "performance": performance_stats
        }
    
    def get_real_time_stats(self, minutes: int = 5) -> Dict:
        """Retorna estatísticas em tempo real"""
        cutoff_time = time.time() - (minutes * 60)
        
        recent_events = [
            event for event in self.events
            if event.timestamp >= cutoff_time
        ]
        
        # Contagens por tipo
        event_counts = defaultdict(int)
        active_users = set()
        active_sessions = set()
        
        for event in recent_events:
            event_counts[event.event_type] += 1
            if event.user_id:
                active_users.add(event.user_id)
            if event.session_id:
                active_sessions.add(event.session_id)
        
        # Eventos mais recentes
        latest_events = sorted(recent_events, key=lambda x: x.timestamp, reverse=True)[:20]
        
        return {
            "period_minutes": minutes,
            "total_events": len(recent_events),
            "active_users": len(active_users),
            "active_sessions": len(active_sessions),
            "event_breakdown": dict(event_counts),
            "latest_events": [
                {
                    "type": e.event_type,
                    "user_id": e.user_id,
                    "timestamp": e.timestamp,
                    "data": e.data
                }
                for e in latest_events
            ]
        }
    
    def get_funnel_analytics(self, days: int = 30) -> Dict:
        """Retorna análise de funil"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        funnel_events = [
            event for event in self.events
            if event.timestamp >= cutoff_time and event.event_type in ["page_view", "search", "filter"]
        ]
        
        # Análise de funil: Visitou → Buscou → Filtrou → Detalhes
        funnel_steps = {
            "visited": len([e for e in funnel_events if e.event_type == "page_view"]),
            "searched": len([e for e in funnel_events if e.event_type == "search"]),
            "filtered": len([e for e in funnel_events if e.event_type == "filter"]),
            "details": len([e for e in funnel_events if e.data.get("action") == "view_details"])
        }
        
        # Taxa de conversão
        total_visitors = len(set(e.user_id for e in funnel_events if e.user_id))
        conversion_rates = {}
        
        if funnel_steps["visited"] > 0:
            conversion_rates["search_rate"] = (funnel_steps["searched"] / funnel_steps["visited"]) * 100
            conversion_rates["filter_rate"] = (funnel_steps["filtered"] / funnel_steps["visited"]) * 100
            conversion_rates["details_rate"] = (funnel_steps["details"] / funnel_steps["visited"]) * 100
        
        return {
            "period_days": days,
            "unique_visitors": total_visitors,
            "funnel_steps": funnel_steps,
            "conversion_rates": conversion_rates
        }
    
    def export_analytics(self, format: str = "json", days: int = 30) -> Dict:
        """Exporta dados de analytics"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        export_events = [
            event for event in self.events
            if event.timestamp >= cutoff_time
        ]
        
        export_data = {
            "export_timestamp": time.time(),
            "period_days": days,
            "total_events": len(export_events),
            "events": [
                {
                    "timestamp": e.timestamp,
                    "datetime": e.datetime.isoformat(),
                    "event_type": e.event_type,
                    "user_id": e.user_id,
                    "session_id": e.session_id,
                    "data": e.data
                }
                for e in export_events
            ]
        }
        
        if format.lower() == "json":
            return {"format": "json", "data": export_data}
        elif format.lower() == "csv":
            # Implementar export CSV se necessário
            return {"format": "csv", "data": "CSV export not implemented yet"}
        else:
            return {"error": "Unsupported format"}
    
    def _calculate_avg_session_duration(self, user_id: str) -> float:
        """Calcula duração média da sessão"""
        user_sessions = [
            session for session_id, session in self.sessions.items()
            if session.get("user_id") == user_id
        ]
        
        if not user_sessions:
            return 0
        
        durations = [
            session.get("duration", 0) for session in user_sessions
            if session.get("duration", 0) > 0
        ]
        
        return sum(durations) / len(durations) if durations else 0

# Instância global
analytics_service = AnalyticsService()
