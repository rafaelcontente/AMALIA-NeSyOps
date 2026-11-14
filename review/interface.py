"""
Interface para revisores humanos: aprovar, corrigir, rejeitar ou pedir info.
Maker-checker: quem gerou não aprova.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from review.queue import ReviewQueue, EscalatedCase

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class HumanDecision(BaseModel):
    """Decisão humana sobre um caso."""
    model_config = ConfigDict(frozen=True)
    
    case_id: str
    reviewer_id: str
    decision: str  # approved, rejected, corrected, request_info
    justification: str
    corrections: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=utc_now)
    trace_id: str

class ReviewInterface:
    """Interface para revisores humanos."""
    
    def __init__(self, queue: ReviewQueue):
        self.queue = queue
        self.decisions: List[HumanDecision] = []
    
    def decide(self, case_id: str, reviewer_id: str, decision: str, 
               justification: str, corrections: Optional[Dict[str, Any]] = None) -> HumanDecision:
        """
        Regista decisão humana sobre um caso.
        Valida maker-checker: quem gerou não aprova.
        """
        case = self.queue.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")
        
        # Maker-checker: quem gerou não aprova
        if reviewer_id == case.proposer_id:
            raise ValueError(f"Maker-checker violado: {reviewer_id} gerou a proposta e não pode aprovar")
        
        # Validar decisão
        valid_decisions = {"approved", "rejected", "corrected", "request_info"}
        if decision not in valid_decisions:
            raise ValueError(f"Decisão inválida: {decision}. Deve ser uma de {valid_decisions}")
        
        # Justificação obrigatória
        if not justification or len(justification.strip()) < 10:
            raise ValueError("Justificação deve ter pelo menos 10 caracteres")
        
        # Criar decisão
        human_decision = HumanDecision(
            case_id=case_id,
            reviewer_id=reviewer_id,
            decision=decision,
            justification=justification,
            corrections=corrections,
            trace_id=case.trace_id
        )
        
        # Atualizar status do caso
        status_map = {
            "approved": "approved",
            "rejected": "rejected",
            "corrected": "corrected",
            "request_info": "pending"  # Volta para fila
        }
        
        self.queue.update_case(case_id, {"status": status_map[decision]})
        
        # Registar decisão
        self.decisions.append(human_decision)
        
        return human_decision
    
    def get_decision(self, case_id: str) -> Optional[HumanDecision]:
        """Retorna decisão para um caso."""
        for decision in self.decisions:
            if decision.case_id == case_id:
                return decision
        return None
    
    def get_decisions_by_trace(self, trace_id: str) -> List[HumanDecision]:
        """Retorna todas as decisões para um trace."""
        return [d for d in self.decisions if d.trace_id == trace_id]
