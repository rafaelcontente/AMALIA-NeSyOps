"""Webhooks para notificacoes assincronas."""
from typing import Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class WebhookEvent(BaseModel):
    event_type: str
    entity_id: str
    trace_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)

class WebhookSubscription(BaseModel):
    subscription_id: str
    entity_id: str
    url: str
    event_types: List[str]
    secret: str = ""
    active: bool = True
    created_at: datetime = Field(default_factory=utc_now)

class WebhookManager:
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.events_sent: List[Dict[str, Any]] = []

    def subscribe(self, subscription: WebhookSubscription):
        self.subscriptions[subscription.subscription_id] = subscription

    def unsubscribe(self, subscription_id: str):
        if subscription_id in self.subscriptions:
            sub = self.subscriptions[subscription_id]
            self.subscriptions[subscription_id] = sub.model_copy(update={"active": False})

    def emit_event(self, event: WebhookEvent):
        """Entrega simulada: regista o envio por subscricao activa do mesmo tenant."""
        for sub in self.subscriptions.values():
            if sub.active and sub.entity_id == event.entity_id and event.event_type in sub.event_types:
                self.events_sent.append({
                    "subscription_id": sub.subscription_id,
                    "url": sub.url,
                    "event": event.model_dump(),
                    "sent_at": utc_now(),
                })

    def get_events_for_subscription(self, subscription_id: str) -> List[Dict[str, Any]]:
        return [e for e in self.events_sent if e["subscription_id"] == subscription_id]
