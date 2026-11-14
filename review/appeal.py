"""Processo de recurso (appeal) para cidadãos."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Appeal(BaseModel):
    """Pedido de recurso de uma decisão."""
    appeal_id: str = Field(default_factory=lambda: str(uuid4()))
    original_trace_id: str
    citizen_id: str
    reason: str
    supporting_evidence: str = ""
    status: str = "pending"  # pending, under_review, approved, rejected
    created_at: datetime = Field(default_factory=utc_now)
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None
    reviewer_decision: Optional[str] = None
    reviewer_rationale: Optional[str] = None


class AppealProcess:
    """
    Gestão de pedidos de recurso.
    
    Invariantes:
    - Um cidadão pode recorrer de uma decisão REJECTED
    - Cada recurso é analisado por um revisor independente
    - O recurso gera um novo trace_id ligado ao original
    """
    
    def __init__(self):
        self.appeals: Dict[str, Appeal] = {}
        self.trace_mapping: Dict[str, str] = {}  # appeal_id -> new_trace_id
    
    def submit_appeal(
        self,
        original_trace_id: str,
        citizen_id: str,
        reason: str,
        supporting_evidence: str = "",
    ) -> Appeal:
        """Submete um pedido de recurso."""
        appeal = Appeal(
            original_trace_id=original_trace_id,
            citizen_id=citizen_id,
            reason=reason,
            supporting_evidence=supporting_evidence,
        )
        self.appeals[appeal.appeal_id] = appeal
        return appeal
    
    def review_appeal(
        self,
        appeal_id: str,
        reviewer_id: str,
        decision: str,
        rationale: str = "",
    ) -> Dict[str, Any]:
        """
        Analisa um recurso.
        
        Returns:
            {"status": "approved"|"rejected", "new_trace_id": "..."}
        """
        if appeal_id not in self.appeals:
            raise ValueError(f"Appeal not found: {appeal_id}")
        
        appeal = self.appeals[appeal_id]
        if appeal.status != "pending":
            return {"status": "error", "error": f"Appeal already {appeal.status}"}
        
        appeal.status = "under_review"
        appeal.reviewed_at = utc_now()
        appeal.reviewer_id = reviewer_id
        appeal.reviewer_decision = decision
        appeal.reviewer_rationale = rationale
        
        # Gerar novo trace_id para o recurso
        new_trace_id = f"APPEAL-{appeal.appeal_id[:8]}"
        self.trace_mapping[appeal.appeal_id] = new_trace_id
        
        if decision == "approved":
            appeal.status = "approved"
        elif decision == "rejected":
            appeal.status = "rejected"
        else:
            appeal.status = "pending"  # Escalado
        
        return {
            "status": appeal.status,
            "new_trace_id": new_trace_id,
            "appeal_id": appeal.appeal_id,
        }
    
    def get_appeal(self, appeal_id: str) -> Optional[Appeal]:
        return self.appeals.get(appeal_id)
    
    def get_appeals_by_citizen(self, citizen_id: str) -> List[Appeal]:
        return [a for a in self.appeals.values() if a.citizen_id == citizen_id]
    
    def get_appeals_by_status(self, status: str) -> List[Appeal]:
        return [a for a in self.appeals.values() if a.status == status]
