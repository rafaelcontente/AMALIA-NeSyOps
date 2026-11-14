"""Explorador de auditoria: linha do tempo e verificação de integridade."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditTimelineEntry(BaseModel):
    """Entrada na linha do tempo de auditoria."""
    timestamp: datetime
    event_type: str
    actor: str
    details: Dict[str, Any]
    trace_id: Optional[str] = None

class AuditExplorer:
    """Explorador de auditoria: linha do tempo e verificação de integridade."""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_timeline(self, trace_id: str) -> List[AuditTimelineEntry]:
        """Obtém linha do tempo de um trace."""
        timeline_data = self.api_client.get_audit_timeline(trace_id)
        
        timeline = []
        for entry_data in timeline_data:
            entry = AuditTimelineEntry(
                timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                event_type=entry_data["event_type"],
                actor=entry_data["actor"],
                details=entry_data["details"],
                trace_id=entry_data.get("trace_id")
            )
            timeline.append(entry)
        
        return timeline
    
    def verify_integrity(self, trace_id: str) -> Dict[str, Any]:
        """Verifica integridade da cadeia de auditoria."""
        result = self.api_client.verify_audit_integrity(trace_id)
        
        return {
            "trace_id": trace_id,
            "valid": result.get("valid", False),
            "broken_at": result.get("broken_at"),
            "message": result.get("message", ""),
            "verified_at": utc_now()
        }
    
    def search_events(self, filters: Dict[str, Any]) -> List[AuditTimelineEntry]:
        """Pesquisa eventos de auditoria com filtros."""
        results = self.api_client.search_audit_events(filters)
        
        timeline = []
        for entry_data in results:
            entry = AuditTimelineEntry(
                timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                event_type=entry_data["event_type"],
                actor=entry_data["actor"],
                details=entry_data["details"],
                trace_id=entry_data.get("trace_id")
            )
            timeline.append(entry)
        
        return timeline
    
    def export_timeline(self, trace_id: str, format: str = "json") -> str:
        """Exporta linha do tempo em formato específico."""
        timeline = self.get_timeline(trace_id)
        
        if format == "json":
            import json
            return json.dumps([entry.model_dump() for entry in timeline], indent=2)
        elif format == "csv":
            lines = ["timestamp,event_type,actor,trace_id"]
            for entry in timeline:
                lines.append(f"{entry.timestamp.isoformat()},{entry.event_type},{entry.actor},{entry.trace_id or ''}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Formato não suportado: {format}")
