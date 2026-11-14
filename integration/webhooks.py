"""Sistema de webhooks para notificações assíncronas."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class WebhookEvent(BaseModel):
    """Evento para enviar via webhook."""
    from pydantic import BaseModel
    
    event_type: str
    entity_id: str
    trace_id: str
    payload: Dict[str, Any]
    timestamp: datetime

from pydantic import BaseModel

class WebhookEvent(BaseModel):
    """Evento para enviar via webhook."""
    event_type: str
    entity_id: str
    trace_id: str
    payload: Dict[str, Any]
    timestamp: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = utc_now()

class WebhookSubscription(BaseModel):
    """Subscrição de webhook."""
    subscription_id: str
    entity_id: str
    url: str
    event_types: List[str]
    secret: str
    active: bool = True
    created_at: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = utc_now()

class WebhookManager:
    """Gestor de webhooks."""
    
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.events_sent: List[Dict[str, Any]] = []
    
    def subscribe(self, subscription: WebhookSubscription):
        """Regista uma subscrição de webhook."""
        self.subscriptions[subscription.subscription_id] = subscription
    
    def unsubscribe(self, subscription_id: str):
        """Remove uma subscrição."""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].active = False
    
    def emit_event(self, event: WebhookEvent):
        """
        Emite um evento para todas as subscrições relevantes.
        
        Em produção, isto faria HTTP POST para os URLs.
        Aqui apenas registamos o evento.
        """
        # Encontrar subscrições relevantes
        relevant_subs = [
            sub for sub in self.subscriptions.values()
            if sub.active and 
               sub.entity_id == event.entity_id and
               event.event_type in sub.event_types
        ]
        
        # Enviar para cada subscrição (simulado)
        for sub in relevant_subs:
            # Em produção: HTTP POST para sub.url com payload e assinatura
            event_record = {
                "subscription_id": sub.subscription_id,
                "url": sub.url,
                "event": event.model_dump(),
                "sent_at": utc_now()
            }
            self.events_sent.append(event_record)
    
    def get_events_for_subscription(self, subscription_id: str) -> List[Dict[str, Any]]:
        """Retorna eventos enviados para uma subscrição."""
        return [
            event for event in self.events_sent
            if event["subscription_id"] == subscription_id
        ]
