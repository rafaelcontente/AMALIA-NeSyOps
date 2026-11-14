"""Maker-Checker: decisões de alto risco exigem aprovação independente."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MakerCheckerDecision(BaseModel):
    """Voto individual de um revisor no processo maker-checker."""
    reviewer_id: str
    decision: str  # "approved", "rejected", "escalated"
    rationale: str = ""
    timestamp: datetime = Field(default_factory=utc_now)


class MakerCheckerPolicy:
    """
    Política maker-checker para decisões de alto risco.
    
    Invariantes:
    - Uma decisão de alto risco requer N aprovações independentes
    - O mesmo revisor não pode votar duas vezes
    - Se houver veto (rejection), a decisão é rejeitada imediatamente
    """
    
    def __init__(self, required_approvals: int = 2):
        self.required_approvals = required_approvals
        self.decisions: Dict[str, List[MakerCheckerDecision]] = {}
    
    def submit_vote(
        self,
        case_id: str,
        reviewer_id: str,
        decision: str,
        rationale: str = "",
    ) -> Dict[str, Any]:
        """
        Submete o voto de um revisor.
        
        Returns:
            {"status": "pending"|"approved"|"rejected", "votes": [...]}
        """
        if decision not in {"approved", "rejected", "escalated"}:
            raise ValueError(f"Invalid decision: {decision}")
        
        votes = self.decisions.setdefault(case_id, [])
        
        # Verificar se já votou
        if any(v.reviewer_id == reviewer_id for v in votes):
            return {"status": "error", "error": "Reviewer already voted"}
        
        vote = MakerCheckerDecision(
            reviewer_id=reviewer_id,
            decision=decision,
            rationale=rationale,
        )
        votes.append(vote)
        
        # Veto imediato: qualquer rejection rejeita a decisão
        if decision == "rejected":
            return {"status": "rejected", "votes": [v.model_dump(mode="json") for v in votes]}
        
        # Contar aprovações
        approvals = sum(1 for v in votes if v.decision == "approved")
        if approvals >= self.required_approvals:
            return {"status": "approved", "votes": [v.model_dump(mode="json") for v in votes]}
        
        return {"status": "pending", "votes": [v.model_dump(mode="json") for v in votes]}
    
    def get_status(self, case_id: str) -> Dict[str, Any]:
        """Retorna o estado atual de uma decisão."""
        votes = self.decisions.get(case_id, [])
        approvals = sum(1 for v in votes if v.decision == "approved")
        rejections = sum(1 for v in votes if v.decision == "rejected")
        
        if rejections > 0:
            status = "rejected"
        elif approvals >= self.required_approvals:
            status = "approved"
        else:
            status = "pending"
        
        return {
            "case_id": case_id,
            "status": status,
            "approvals": approvals,
            "rejections": rejections,
            "required": self.required_approvals,
            "votes": [v.model_dump(mode="json") for v in votes],
        }
    
    def reset(self, case_id: str):
        """Reseta uma decisão (apenas para testes)."""
        self.decisions.pop(case_id, None)
