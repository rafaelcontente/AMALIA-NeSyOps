"""
Kill switch: passa o sistema para modo seguro (escalar ou recusar).
Quando ativo, nenhuma decisão automática sai do sistema.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class SafeMode(str, Enum):
    ESCALATE = "escalate"  # Encaminhar tudo para revisão humana
    REJECT = "reject"      # Recusar tudo

class KillSwitch:
    """Interruptor global de segurança."""
    
    def __init__(self):
        self._active = False
        self._safe_mode = SafeMode.ESCALATE
        self._reason: Optional[str] = None
        self._activated_at: Optional[datetime] = None
        self._activated_by: Optional[str] = None
        self._history: list = []
    
    @property
    def active(self) -> bool:
        return self._active
    
    @property
    def safe_mode(self) -> SafeMode:
        return self._safe_mode
    
    def activate(self, reason: str, activated_by: str, 
                 mode: SafeMode = SafeMode.ESCALATE) -> Dict[str, Any]:
        """Ativa o kill switch."""
        if self._active:
            return {"status": "already_active", "reason": self._reason}
        
        self._active = True
        self._safe_mode = mode
        self._reason = reason
        self._activated_at = utc_now()
        self._activated_by = activated_by
        
        # Registar no histórico
        self._history.append({
            "action": "activated",
            "reason": reason,
            "mode": mode.value,
            "by": activated_by,
            "timestamp": self._activated_at.isoformat()
        })
        
        return {
            "status": "activated",
            "mode": mode.value,
            "reason": reason,
            "timestamp": self._activated_at.isoformat()
        }
    
    def deactivate(self, deactivated_by: str, reason: str = "") -> Dict[str, Any]:
        """Desativa o kill switch."""
        if not self._active:
            return {"status": "already_inactive"}
        
        deactivated_at = utc_now()
        
        # Registar no histórico
        self._history.append({
            "action": "deactivated",
            "reason": reason,
            "by": deactivated_by,
            "timestamp": deactivated_at.isoformat()
        })
        
        self._active = False
        self._reason = None
        self._activated_at = None
        self._activated_by = None
        
        return {
            "status": "deactivated",
            "reason": reason,
            "timestamp": deactivated_at.isoformat()
        }
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um pedido aplicando o kill switch se ativo.
        Retorna: {"mode": str, "action": str, ...}
        """
        if not self._active:
            return {"mode": "normal", "action": "process"}
        
        if self._safe_mode == SafeMode.ESCALATE:
            return {
                "mode": "safe",
                "action": "escalate",
                "reason": self._reason,
                "activated_by": self._activated_by
            }
        else:  # REJECT
            return {
                "mode": "safe",
                "action": "reject",
                "reason": self._reason,
                "activated_by": self._activated_by
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual."""
        return {
            "active": self._active,
            "safe_mode": self._safe_mode.value if self._active else None,
            "reason": self._reason,
            "activated_at": self._activated_at.isoformat() if self._activated_at else None,
            "activated_by": self._activated_by,
            "history": self._history
        }
