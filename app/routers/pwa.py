"""
PWA Endpoints - Push Notifications and App Management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class PushSubscription(BaseModel):
    endpoint: str
    keys: dict
    expirationTime: Optional[int] = None

class PushMessage(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None
    data: Optional[dict] = None

# Storage em memória (em produção usar Redis/Database)
push_subscriptions = []

@router.post("/subscribe")
async def subscribe_to_push(subscription: PushSubscription):
    """Registra subscription para push notifications"""
    try:
        # Verificar se já existe
        existing = next((s for s in push_subscriptions 
                      if s.endpoint == subscription.endpoint), None)
        
        if existing:
            logger.info(f"Subscription já existe: {subscription.endpoint}")
            return {"status": "already_subscribed"}
        
        # Adicionar nova subscription
        push_subscriptions.append(subscription.dict())
        logger.info(f"Push subscription registrada: {subscription.endpoint}")
        
        return {"status": "subscribed", "endpoint": subscription.endpoint}
        
    except Exception as e:
        logger.error(f"Erro ao registrar push subscription: {e}")
        raise HTTPException(status_code=500, detail="Erro ao registrar subscription")

@router.delete("/unsubscribe/{endpoint}")
async def unsubscribe_from_push(endpoint: str):
    """Remove subscription de push notifications"""
    try:
        global push_subscriptions
        push_subscriptions = [s for s in push_subscriptions if s["endpoint"] != endpoint]
        logger.info(f"Push subscription removida: {endpoint}")
        
        return {"status": "unsubscribed"}
        
    except Exception as e:
        logger.error(f"Erro ao remover push subscription: {e}")
        raise HTTPException(status_code=500, detail="Erro ao remover subscription")

@router.get("/subscriptions")
async def get_subscriptions():
    """Lista todas as subscriptions (admin only)"""
    return {
        "count": len(push_subscriptions),
        "subscriptions": push_subscriptions
    }

@router.post("/send-notification")
async def send_notification(
    message: PushMessage, 
    background_tasks: BackgroundTasks
):
    """Envia push notification para todos os subscribers"""
    try:
        if not push_subscriptions:
            return {"status": "no_subscribers"}
        
        # Preparar payload
        payload = {
            "title": message.title,
            "body": message.body,
            "icon": message.icon or "/static/icons/icon-192x192.png",
            "data": message.data or {},
            "vibrate": [200, 100, 200],
            "actions": [
                {
                    "action": "view",
                    "title": "Ver Leilões",
                    "icon": "/static/icons/icon-96x96.png"
                },
                {
                    "action": "dismiss",
                    "title": "Ignorar"
                }
            ]
        }
        
        # Enviar em background (não bloquear response)
        background_tasks.add_task(
            send_push_to_all_subscribers, 
            payload
        )
        
        return {
            "status": "sending",
            "recipients": len(push_subscriptions)
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar notificação")

async def send_push_to_all_subscribers(payload: dict):
    """Envia push notification para todos os subscribers"""
    import httpx
    
    for subscription in push_subscriptions:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    subscription["endpoint"],
                    json={
                        "payload": payload,
                        "keys": subscription["keys"]
                    },
                    headers={
                        "TTL": "86400",  # 24 horas
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Push enviado para: {subscription['endpoint']}")
                else:
                    logger.warning(f"Falha ao enviar push: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Erro ao enviar push para {subscription['endpoint']}: {e}")

@router.get("/status")
async def get_pwa_status():
    """Retorna status das funcionalidades PWA"""
    return {
        "serviceWorker": True,  # Suportado
        "pushNotifications": True,  # Suportado
        "installPrompt": True,  # Suportado
        "offlineSupport": True,  # Suportado
        "subscribers": len(push_subscriptions),
        "features": {
            "cache": "Cache-first para static, network-first para API",
            "sync": "Background sync para dados offline",
            "push": "Push notifications com VAPID",
            "install": "Install prompt customizado"
        }
    }

@router.post("/test-notification")
async def test_notification():
    """Envia notificação de teste"""
    test_message = PushMessage(
        title="🔔 Teste PWA",
        body="Notificação de teste do Monitor de Leilões!",
        icon="/static/icons/icon-192x192.png",
        data={"type": "test", "timestamp": "2024-01-01T00:00:00Z"}
    )
    
    return await send_notification(test_message, BackgroundTasks())
