"""
Modelo de entrada de auditoria.
Cada entrada é imutável e contém todos os metadados necessários para replay.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditEntry(BaseModel):
    """Entrada de auditoria imutável."""
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    
    # Versões do sistema (AIBOM - AI Bill of Materials)
    model_version: str
    prompt_version: str
    rules_version: str
    schema_version: str
    
    # Entrada (ou referência pseudonimizada para RGPD)
    input_data: Dict[str, Any]
    input_pseudonym: Optional[str] = None  # Hash do input original
    
    # Ferramentas chamadas
    tools_called: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Regras avaliadas
    rules_evaluated: List[str] = Field(default_factory=list)
    rules_violated: List[str] = Field(default_factory=list)
    
    # Saída real do LLM (não se conta com reproduzi-la)
    llm_output: Optional[str] = None
    
    # Decisão final
    decision: Dict[str, Any]
    
    # Intervenção humana
    human_reviewer: Optional[str] = None
    human_decision: Optional[str] = None
    
    # Hash chain
    previous_hash: Optional[str] = None
    entry_hash: str = ""
    
    # Prazo de retenção (RGPD)
    retention_until: Optional[datetime] = None
    
    def compute_hash(self) -> str:
        """Calcula o hash desta entrada (excluindo previous_hash e entry_hash)."""
        data = {
            "id": self.id,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "model_version": self.model_version,
            "prompt_version": self.prompt_version,
            "rules_version": self.rules_version,
            "schema_version": self.schema_version,
            "input_data": self.input_data,
            "input_pseudonym": self.input_pseudonym,
            "tools_called": self.tools_called,
            "rules_evaluated": self.rules_evaluated,
            "rules_violated": self.rules_violated,
            "llm_output": self.llm_output,
            "decision": self.decision,
            "human_reviewer": self.human_reviewer,
            "human_decision": self.human_decision,
            "previous_hash": self.previous_hash,
            "retention_until": self.retention_until.isoformat() if self.retention_until else None
        }
        json_str = json.dumps(data, sort_keys=True, default=str)
        import hashlib
        return hashlib.sha256(json_str.encode()).hexdigest()
