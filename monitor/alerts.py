"""
Sistema de alertas com thresholds e cooldown.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AlertSeverity:
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class Alert:
    def __init__(self, alert_id: str, severity: str, message: str, 
                 source: str, details: Dict[str, Any] = None):
        self.alert_id = alert_id
        self.severity = severity
        self.message = message
        self.source = source
        self.details = details or {}
        self.timestamp = utc_now()
        self.acknowledged = False
    
    def to_dict(self):
        return {
            "alert_id": self.alert_id,
            "severity": self.severity,
            "message": self.message,
            "source": self.source,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged
        }

class AlertManager:
    """Gestor de alertas com cooldown."""
    
    def __init__(self, cooldown_minutes: int = 60):
        self.alerts: List[Alert] = []
        self._last_alert_time: Dict[str, datetime] = {}
        self.cooldown = timedelta(minutes=cooldown_minutes)
    
    def raise_alert(self, alert_id: str, severity: str, message: str,
                    source: str, details: Dict[str, Any] = None,
                    force: bool = False) -> Optional[Alert]:
        """
        Levanta um alerta (respeita cooldown).
        Se force=True, ignora cooldown.
        """
        # Verificar cooldown
        if not force and alert_id in self._last_alert_time:
            last_time = self._last_alert_time[alert_id]
            if utc_now() - last_time < self.cooldown:
                return None  # Ainda em cooldown
        
        # Criar alerta
        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            message=message,
            source=source,
            details=details
        )
        
        self.alerts.append(alert)
        self._last_alert_time[alert_id] = alert.timestamp
        
        return alert
    
    def get_active_alerts(self) -> List[Alert]:
        """Retorna alertas não reconhecidos."""
        return [a for a in self.alerts if not a.acknowledged]
    
    def get_critical_alerts(self) -> List[Alert]:
        """Retorna alertas críticos."""
        return [a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]
    
    def acknowledge(self, alert_id: str) -> bool:
        """Reconhece um alerta."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
