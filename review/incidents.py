"""Gestão de incidentes e runbooks."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Incident(BaseModel):
    """Registo de incidente."""
    incident_id: str = Field(default_factory=lambda: str(uuid4()))
    severity: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    affected_component: str
    status: str = "open"  # open, investigating, resolved, closed
    created_at: datetime = Field(default_factory=utc_now)
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    runbook_followed: Optional[str] = None


# Runbooks predefinidos
RUNBOOKS = {
    "kill_switch_activated": {
        "title": "Kill Switch Ativado",
        "steps": [
            "1. Verificar logs em monitor/ para identificar trigger",
            "2. Confirmar que todas as decisões estão a ser rejeitadas",
            "3. Notificar equipa de operações e DPO",
            "4. Analisar causa raiz (drift, injection, falha de modelo)",
            "5. Corrigir causa e desativar kill switch manualmente",
            "6. Documentar incidente e lições aprendidas",
        ],
    },
    "audit_chain_broken": {
        "title": "Cadeia de Auditoria Quebrada",
        "steps": [
            "1. Executar audit/integrity.py::IntegrityChecker.verify_integrity()",
            "2. Identificar entry_id onde a cadeia quebrou",
            "3. Verificar se foi adulteração ou bug de software",
            "4. Se adulteração: notificar segurança e DPO imediatamente",
            "5. Se bug: corrigir e reconstruir cadeia a partir do último válido",
            "6. Documentar e atualizar testes de regressão",
        ],
    },
    "llm_hallucination_detected": {
        "title": "Alucinação de LLM Detetada",
        "steps": [
            "1. Isolar o caso em review/appeal.py para análise",
            "2. Verificar HallucinationChecker logs",
            "3. Identificar entidade fictícia no grafo de conhecimento",
            "4. Atualizar grafo se a entidade for válida mas faltante",
            "5. Re-treinar ou ajustar prompt se for padrão recorrente",
            "6. Documentar caso em regression/cases/",
        ],
    },
    "circuit_breaker_open": {
        "title": "Circuit Breaker do LLM Aberto",
        "steps": [
            "1. Verificar saúde do Ollama: agents/ollama_adapter.py::is_healthy()",
            "2. Se Ollama down: reiniciar serviço ou mudar para fallback",
            "3. Se falhas intermitentes: aumentar timeout ou reduzir carga",
            "4. Monitorizar métricas em integration/observability.py",
            "5. Fechar circuit breaker manualmente após recuperação",
            "6. Documentar causa e duração do incidente",
        ],
    },
}


class IncidentManager:
    """Gestão de incidentes com runbooks."""
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
    
    def report_incident(
        self,
        severity: str,
        title: str,
        description: str,
        affected_component: str,
    ) -> Incident:
        """Reporta um novo incidente."""
        if severity not in {"critical", "high", "medium", "low"}:
            raise ValueError(f"Invalid severity: {severity}")
        
        incident = Incident(
            severity=severity,
            title=title,
            description=description,
            affected_component=affected_component,
        )
        self.incidents[incident.incident_id] = incident
        return incident
    
    def resolve_incident(
        self,
        incident_id: str,
        resolution: str,
        runbook_followed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolve um incidente."""
        if incident_id not in self.incidents:
            raise ValueError(f"Incident not found: {incident_id}")
        
        incident = self.incidents[incident_id]
        incident.status = "resolved"
        incident.resolved_at = utc_now()
        incident.resolution = resolution
        incident.runbook_followed = runbook_followed
        
        return {
            "incident_id": incident_id,
            "status": "resolved",
            "resolution": resolution,
            "runbook_followed": runbook_followed,
        }
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        return self.incidents.get(incident_id)
    
    def get_open_incidents(self) -> List[Incident]:
        return [i for i in self.incidents.values() if i.status in {"open", "investigating"}]
    
    def get_runbook(self, runbook_name: str) -> Optional[Dict[str, Any]]:
        return RUNBOOKS.get(runbook_name)
    
    def list_runbooks(self) -> List[str]:
        return list(RUNBOOKS.keys())
